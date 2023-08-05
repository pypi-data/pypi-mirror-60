# -*- coding: utf-8 -*-

"""A node or step for LAMMPS in a flowchart"""

import argparse
import configargparse
import cpuinfo
import datetime
import glob
import lammps_step
import logging
import math
import seamm
from seamm import data
from seamm_util import ureg, Q_, units_class  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __
import os
import os.path
import pandas
import pprint
import statsmodels.stats.stattools
import statsmodels.api
import statsmodels.tools
from statsmodels.graphics.tsaplots import plot_acf
import sys
import warnings

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as pyplot  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter('lammps')


def upcase(string):
    """Return an uppercase version of the string.

    Used for the type argument in argparse/
    """
    return string.upper()


bond_style = {
    'quadratic_bond': 'harmonic',
    'quartic_bond': 'class2',
    'fene': 'fene',
    'morse': 'morse',
}

angle_style = {
    'quadratic_angle': 'harmonic',
    'quartic_angle': 'class2',
}

dihedral_style = {
    'torsion_1': 'harmonic',
    'torsion_3': 'class2',
}

improper_style = {
    'wilson_out_of_plane': 'class2',
}

lammps_units = {
    'real':
        {
            '[mass]': 'g/mol',
            '[distance]': 'Å',
            '[time]': 'fs',
            '[length] ** 2 * [mass] / [substance] / [time] ** 2': 'kcal/mol',
            '[length] ** 2 * [mass] / [time] ** 2': 'kcal/mol',
            '[length] / [time]': 'Å/fs',
            '[length] * [mass] / [substance] / [time] ** 2': 'kcal/mol/Å',
            '[length] * [mass] / [time] ** 2': 'kcal/mol/Å',
            '[temperature]': 'K',
            '[mass] / [length] / [time] ** 2': 'bar',
            '[mass] / [length] / [time]': 'poise',
            '[current] * [time]': 'e',
            '[current] * [length] * [time]': 'e*Å',
            '[length] * [mass] / [current] / [time] ** 3': 'V/Å',
            '[mass] / [length] ** 3': 'g/mL'
        },
    'metal':
        {
            '[mass]': 'g/mol',
            '[distance]': 'Å',
            '[time]': 'ps',
            '[length] ** 2 * [mass] / [substance] / [time] ** 2': 'eV',
            '[length] ** 2 * [mass] / [time] ** 2': 'eV',
            '[length] / [time]': 'Å/ps',
            '[length] * [mass] / [substance] / [time] ** 2': 'eV/Å',
            '[length] * [mass] / [time] ** 2': 'eV/Å',
            '[temperature]': 'K',
            '[mass] / [length] / [time] ** 2': 'atm',
            '[mass] / [length] / [time]': 'poise',
            '[current] * [time]': 'e',
            '[current] * [length] * [time]': 'e*Å',
            '[length] * [mass] / [current] / [time] ** 3': 'V/Å',
            '[mass] / [length] ** 3': 'g/mL'
        }
}


def cosine(degrees):
    return math.cos(math.radians(degrees))


class LAMMPS(seamm.Node):
    display_units = {
        "T": "K",
        "P": "atm",
        "t": "fs",
        "density": "g/mL",
        "a": "Å",
        "b": "Å",
        "c": "Å",
        "Etot": "kcal/mol",
        "Eke": "kcal/mol",
        "Epe": "kcal/mol",
        "Emol": "kcal/mol",
        "Epair": "kcal/mol",
    }

    def __init__(
        self,
        flowchart=None,
        namespace='org.molssi.seamm.lammps',
        extension=None
    ):
        """Setup the main LAMMPS step

        Keyword arguments:
        """
        logger.debug('Creating LAMMPS {}'.format(self))

        # Argument/config parsing
        self.parser = configargparse.ArgParser(
            auto_env_var_prefix='',
            default_config_files=[
                '/etc/seamm/lammps.ini',
                '/etc/seamm/lammps_step.ini',
                '/etc/seamm/seamm.ini',
                '~/.seamm/lammps.ini',
                '~/.seamm/lammps_step.ini',
                '~/.seamm/seamm.ini',
            ]
        )

        self.parser.add_argument(
            '--seamm-configfile',
            is_config_file=True,
            default=None,
            help='a configuration file to override others'
        )

        # Options for this plugin
        self.parser.add_argument(
            "--lammps-log-level",
            default=argparse.SUPPRESS,
            choices=[
                'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
            ],
            type=upcase,
            help="the logging level for the LAMMPS step"
        )

        # General SEAMM options
        self.parser.add_argument(
            '--seamm-use-mpi',
            action='store_true',
            help='use mpi if this flag is present'
        )
        self.parser.add_argument(
            '--seamm-mpi-np',
            default=argparse.SUPPRESS,
            help='how many mpi processes to use'
        )
        self.parser.add_argument(
            '--seamm-mpi-max-np',
            default=argparse.SUPPRESS,
            help='maximum number of mpi processes to use'
        )
        self.parser.add_argument(
            '--seamm-mpiexec',
            default=argparse.SUPPRESS,
            help='the mpiexec command to use'
        )

        # LAMMPS specific options
        self.parser.add_argument(
            '--lammps-use-mpi',
            action='store_true',
            help='whether to use mpi for LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-mpi-np',
            default=argparse.SUPPRESS,
            help='how many mpi processes to use for LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-mpi-max-np',
            default=argparse.SUPPRESS,
            help='maximum number of mpi processes to use for LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-mpiexec',
            default=argparse.SUPPRESS,
            help='the mpiexec command to use for LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-serial',
            default='lmp_serial',
            help='the serial version of LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-mpi',
            default='lmp_mpi',
            help='the mpi version of LAMMPS'
        )
        self.parser.add_argument(
            '--lammps-atoms-per-core',
            type=int,
            default='1000',
            help='the optimal number of atoms per core for LAMMPS'
        )

        self.options, self.unknown = self.parser.parse_known_args()

        # Set the logging level for this module if requested
        if 'lammps_log_level' in self.options:
            logger.setLevel(self.options.lammps_log_level)

        # The subflowchart
        self.subflowchart = seamm.Flowchart(
            parent=self, name='LAMMPS', namespace=namespace
        )
        self.lammps_units = 'real'
        self._data = {}

        self.maxlags = 100

        super().__init__(
            flowchart=flowchart, title='LAMMPS', extension=extension
        )

    @property
    def version(self):
        """The semantic version of this module.
        """
        return lammps_step.__version__

    @property
    def git_revision(self):
        """The git version of this module.
        """
        return lammps_step.__git_revision__

    def set_id(self, node_id):
        """Set the id for node to a given tuple"""
        self._id = node_id

        # and set our subnodes
        self.subflowchart.set_ids(self._id)

        return self.next()

    def description_text(self, P=None):
        """Return a short description of this step.

        Return a nicely formatted string describing what this step will
        do.

        Keyword arguments:
            P: a dictionary of parameter values, which may be variables
                or final values. If None, then the parameters values will
                be used as is.
        """

        self.subflowchart.root_directory = self.flowchart.root_directory

        # Get the first real node
        node = self.subflowchart.get_node('1').next()

        text = self.header + '\n\n'
        while node is not None:
            try:
                text += __(node.description_text(), indent=3 * ' ').__str__()
            except Exception as e:
                print(
                    'Error describing LAMMPS flowchart: {} in {}'.format(
                        str(e), str(node)
                    )
                )
                logger.critical(
                    'Error describing LAMMPS flowchart: {} in {}'.format(
                        str(e), str(node)
                    )
                )
                raise
            except:  # noqa: E722
                print(
                    "Unexpected error describing LAMMPS flowchart: {} in {}"
                    .format(sys.exc_info()[0], str(node))
                )
                logger.critical(
                    "Unexpected error describing LAMMPS flowchart: {} in {}"
                    .format(sys.exc_info()[0], str(node))
                )
                raise
            text += '\n'
            node = node.next()

        return text

    def run(self):
        """Run a LAMMPS simulation
        """

        if data.structure is None:
            logger.error('LAMMPS run(): there is no structure!')
            raise RuntimeError('LAMMPS run(): there is no structure!')

        next_node = super().run(printer)

        # Parse the options
        o = self.options

        # Whether to run parallel and if so, how many mpi processes
        use_mpi = 'lammps_use_mpi' in o or 'seamm_use_mpi' in o
        if use_mpi:
            if 'seamm_mpi_np' in o:
                np = o.seamm_mpi_np
            elif 'lammps_mpi_np' in o:
                np = o.lammps_mpi_np
            else:
                np = 'default'

            if np == 'default':
                atoms = seamm.data.structure['atoms']
                n_atoms = len(atoms['elements'])
                np = int(round(n_atoms / o.lammps_atoms_per_core))
                if np < 1:
                    np = 1
            else:
                np = int(np)

            if np == 1:
                use_mpi = False
            else:
                if 'seamm_mpi_max_np' in o:
                    max_np = o.seamm_mpi_max_np
                elif 'lammps_mpi_max_np' in o:
                    max_np = o.lammps_mpi_max_np
                else:
                    max_np = 'default'

                if max_np == 'default':
                    # How many processors does this node have?
                    info = cpuinfo.get_cpu_info()
                    max_np = info['count']
                    # Account for Intel hyperthreading
                    if info['arch'][0:3] == 'X86':
                        max_np = int(max_np / 2)
                logger.info(
                    'The maximum number of cores to use is {}'.format(max_np)
                )

        if use_mpi:
            if 'lammps_mpiexec' in o:
                mpiexec = o.lammps_mpiexec
            elif 'seamm_mpiexec' in o:
                mpiexec = o.seamm_mpiexec
            else:
                use_mpi = False

        # Print headers and get to work
        printer.important(self.header)
        if use_mpi:
            printer.important(
                '   LAMMPS using MPI with {} processes.\n'.format(np)
            )
        else:
            printer.important('   LAMMPS using the serial version.\n')

        logger.info('\n' + 80 * '-' + '\n' + self.parser.format_help())
        logger.info('\n' + 80 * '-' + '\n' + self.parser.format_values())

        self.subflowchart.root_directory = self.flowchart.root_directory

        # Get the first real node
        node = self.subflowchart.get_node('1').next()

        input_data = []
        while node is not None:
            if isinstance(node, lammps_step.Initialization):
                try:
                    lines, eex = node.get_input()
                except Exception as e:
                    print(
                        'Error running LAMMPS flowchart: {} in {}'.format(
                            str(e), str(node)
                        )
                    )
                    logger.critical(
                        'Error running LAMMPS flowchart: {} in {}'.format(
                            str(e), str(node)
                        )
                    )
                    raise
                except:  # noqa: E722
                    print(
                        "Unexpected error running LAMMPS flowchart: {} in {}"
                        .format(sys.exc_info()[0], str(node))
                    )
                    logger.critical(
                        "Unexpected error running LAMMPS flowchart: {} in {}"
                        .format(sys.exc_info()[0], str(node))
                    )
                    raise
                input_data += lines
            else:
                try:
                    input_data += node.get_input()
                except Exception as e:
                    print(
                        'Error running LAMMPS flowchart: {} in {}'.format(
                            str(e), str(node)
                        )
                    )
                    logger.critical(
                        'Error running LAMMPS flowchart: {} in {}'.format(
                            str(e), str(node)
                        )
                    )
                    raise
                except:  # noqa: E722
                    print(
                        "Unexpected error running LAMMPS flowchart: {} in {}"
                        .format(sys.exc_info()[0], str(node))
                    )
                    logger.critical(
                        "Unexpected error running LAMMPS flowchart: {} in {}"
                        .format(sys.exc_info()[0], str(node))
                    )
                    raise
            node = node.next()

        files = {'molssi.dat': '\n'.join(input_data)}
        logger.debug('molssi.dat:\n' + files['molssi.dat'])

        # Get the structure file from the eex
        files['structure.dat'] = '\n'.join(self.structure_data(eex))
        logger.debug('structure.dat:\n' + files['structure.dat'])

        os.makedirs(self.directory, exist_ok=True)
        for filename in files:
            with open(os.path.join(self.directory, filename), mode='w') as fd:
                fd.write(files[filename])
        local = seamm.ExecLocal()
        return_files = ['summary_*.txt', 'trajectory_*.txt']
        if use_mpi:
            cmd = [mpiexec, '-np', str(np), o.lammps_mpi, '-in', 'molssi.dat']
        else:
            cmd = [o.lammps_serial, '-in', 'molssi.dat']

        result = local.run(cmd=cmd, files=files, return_files=return_files)

        if result is None:
            logger.error('There was an error running LAMMPS')
            return None

        logger.debug('\n' + pprint.pformat(result))

        logger.debug('stdout:\n' + result['stdout'])
        with open(os.path.join(self.directory, 'stdout.txt'), mode='w') as fd:
            fd.write(result['stdout'])

        if result['stderr'] != '':
            logger.warning('stderr:\n' + result['stderr'])
            with open(
                os.path.join(self.directory, 'stderr.txt'), mode='w'
            ) as fd:
                fd.write(result['stderr'])

        for filename in result['files']:
            with open(os.path.join(self.directory, filename), mode='w') as fd:
                if result[filename]['data'] is not None:
                    fd.write(result[filename]['data'])
                else:
                    fd.write(result[filename]['exception'])

        # Analyze the results
        self.analyze()

        return next_node

    def structure_data(self, eex, triclinic=False):
        """Create the LAMMPS structure file from the energy expression"""
        lines = []
        lines.append(
            'Structure file for LAMMPS generated by a MolSSI flowchart'
        )
        lines.append('{:10d} atoms'.format(eex['n_atoms']))
        lines.append('{:10d} atom types'.format(eex['n_atom_types']))
        if eex['n_bonds'] > 0:
            lines.append('{:10d} bonds'.format(eex['n_bonds']))
            lines.append('{:10d} bond types'.format(eex['n_bond_types']))
        if eex['n_angles'] > 0:
            lines.append('{:10d} angles'.format(eex['n_angles']))
            lines.append('{:10d} angle types'.format(eex['n_angle_types']))
        if eex['n_torsions'] > 0:
            lines.append('{:10d} dihedrals'.format(eex['n_torsions']))
            lines.append(
                '{:10d} dihedral types'.format(eex['n_torsion_types'])
            )
        if eex['n_oops'] > 0:
            lines.append('{:10d} impropers'.format(eex['n_oops']))
            lines.append('{:10d} improper types'.format(eex['n_oop_types']))

        # Find the box limits
        periodicity = eex['periodicity']
        if periodicity == 3:
            a, b, c, alpha, beta, gamma = eex['cell']
            lx = a
            xy = b * cosine(gamma)
            xz = c * cosine(beta)
            ly = math.sqrt(b**2 - xy**2)
            yz = (b * c * cosine(alpha) - xy * xz) / ly
            lz = math.sqrt(c**2 - xz**2 - yz**2)

            lines.append('{} {} xlo xhi'.format(0.0, lx))
            lines.append('{} {} ylo yhi'.format(0.0, ly))
            lines.append('{} {} zlo zhi'.format(0.0, lz))

            xy = xy if abs(xy) > 1.0e-06 else 0.0
            xz = xz if abs(xy) > 1.0e-06 else 0.0
            yz = yz if abs(xy) > 1.0e-06 else 0.0

            if triclinic or xy > 0.0 or xz > 0.0 or yz > 0.0:
                lines.append('{} {} {} xy xz yz'.format(xy, xz, yz))
        else:
            x, y, z, index = eex['atoms'][0]
            xlo = xhi = x
            ylo = yhi = y
            zlo = zhi = z
            for x, y, z, index in eex['atoms']:
                xlo = x if x < xlo else xlo
                xhi = x if x > xhi else xlo
                ylo = y if y < ylo else ylo
                yhi = y if y > yhi else ylo
                zlo = z if z < zlo else zlo
                zhi = z if z > zhi else zlo

            # Some extra space....
            xlo -= 10.0
            xhi += 10.0
            ylo -= 10.0
            yhi += 10.0
            zlo -= 10.0
            zhi += 10.0

            lines.append('{} {} xlo xhi'.format(xlo, xhi))
            lines.append('{} {} ylo yhi'.format(ylo, yhi))
            lines.append('{} {} zlo zhi'.format(zlo, zhi))

        # the atoms and their masses, etc.
        lines.append('')
        lines.append('Atoms')
        lines.append('')

        for i, xyz_index, q in zip(
            range(1, eex['n_atoms'] + 1), eex['atoms'], eex['charges']
        ):
            x, y, z, index = xyz_index
            lines.append(
                '{:6d} {:6d} {:6d} {:6.3f} {:12.7f} {:12.7f} {:12.7f}'.format(
                    i, 1, index, q, x, y, z
                )
            )
        lines.append('')

        lines.append('Masses')
        lines.append('')
        for i, parameters in zip(
            range(1, eex['n_atom_types'] + 1), eex['masses']
        ):
            mass, itype = parameters
            lines.append('{:6d} {} # {}'.format(i, mass, itype))

        # nonbonds
        lines.append('')
        lines.append('Pair Coeffs')
        lines.append('')
        for i, parameters in zip(
            range(1, eex['n_atom_types'] + 1), eex['nonbond parameters']
        ):
            form, values, types, parameters_type, real_types = \
                parameters
            lines.append(
                '{:6d} {} {} # {} --> {}'.format(
                    i, values['eps'], values['r'], types[0], real_types[0]
                )
            )

        # bonds
        if eex['n_bonds'] > 0:
            lines.append('')
            lines.append('Bonds')
            lines.append('')
            for counter, tmp in zip(
                range(1, eex['n_bonds'] + 1), eex['bonds']
            ):
                i, j, index = tmp
                lines.append(
                    '{:6d} {:6d} {:6d} {:6d}'.format(counter, index, i, j)
                )

            lines.append('')
            lines.append('Bond Coeffs')
            lines.append('')
            for counter, parameters in zip(
                range(1, eex['n_bond_types'] + 1), eex['bond parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                if form == 'quadratic_bond':
                    lines.append(
                        '{:6d} harmonic {} {}'
                        .format(counter, values['K2'], values['R0']) +
                        ' # {}-{} --> {}-{}'.format(
                            types[0], types[1], real_types[0], real_types[1]
                        )
                    )
                elif form == 'quartic_bond':
                    lines.append(
                        '{:6d} class2 {} {} {} {}'.format(
                            counter, values['R0'], values['K2'], values['K3'],
                            values['K4']
                        ) + ' # {}-{} --> {}-{}'.format(
                            types[0], types[1], real_types[0], real_types[1]
                        )
                    )

        # angles
        if eex['n_angles'] > 0:
            lines.append('')
            lines.append('Angles')
            lines.append('')
            for counter, tmp in zip(
                range(1, eex['n_angles'] + 1), eex['angles']
            ):
                i, j, k, index = tmp
                lines.append(
                    '{:6d} {:6d} {:6d} {:6d} {:6d}'.format(
                        counter, index, i, j, k
                    )
                )

            lines.append('')
            lines.append('Angle Coeffs')
            lines.append('')
            for counter, parameters in zip(
                range(1, eex['n_angle_types'] + 1), eex['angle parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                if form == 'quadratic_angle':
                    lines.append(
                        '{:6d} harmonic {} {}'
                        .format(counter, values['K2'], values['Theta0']) +
                        ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )
                elif form == 'quartic_angle':
                    lines.append(
                        '{:6d} class2 {} {} {} {}'.format(
                            counter, values['Theta0'], values['K2'],
                            values['K3'], values['K4']
                        ) + ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )

            # bond-bond coefficients, which must match angles in order & number
            lines.append('')
            lines.append('BondBond Coeffs')
            lines.append('')
            for counter, parameters, angles in zip(
                range(1, eex['n_bond-bond_types'] + 1),
                eex['bond-bond parameters'], eex['angle parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                angle_form = angles[0]
                if angle_form == 'quartic_angle':
                    lines.append(
                        '{:6d} class2 {} {} {}'.format(
                            counter, values['K'], values['R10'], values['R20']
                        ) + ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )

            # bond-angles coefficients, which must match angles in order &
            # number
            lines.append('')
            lines.append('BondAngle Coeffs')
            lines.append('')
            for counter, parameters, angles in zip(
                range(1, eex['n_bond-angle_types'] + 1),
                eex['bond-angle parameters'], eex['angle parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                angle_form = angles[0]
                if angle_form == 'quartic_angle':
                    lines.append(
                        '{:6d} class2 {} {} {} {}'.format(
                            counter, values['K12'], values['K23'],
                            values['R10'], values['R20']
                        ) + ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{} --> {}-{}-{}'.format(
                            types[0], types[1], types[2], real_types[0],
                            real_types[1], real_types[2]
                        )
                    )

        # torsions
        if eex['n_torsions'] > 0:
            lines.append('')
            lines.append('Dihedrals')
            lines.append('')
            for counter, tmp in zip(
                range(1, eex['n_torsions'] + 1), eex['torsions']
            ):
                i, j, k, l, index = tmp
                lines.append(
                    '{:6d} {:6d} {:6d} {:6d} {:6d} {:6d}'.format(
                        counter, index, i, j, k, l
                    )
                )

            lines.append('')
            lines.append('Dihedral Coeffs')
            lines.append('')
            for counter, parameters in zip(
                range(1, eex['n_torsion_types'] + 1), eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                if form == 'torsion_1':
                    KPhi = values['KPhi']
                    n = values['n']
                    Phi0 = values['Phi0']

                    # Discover form is
                    #  KPhi * [1 + cos(n*Phi - Phi0)]
                    #  with trans = 180
                    #
                    #  For ethane, Phi0 = 0 so at Phi=180 E is min. Correct

                    # Lammps for is
                    #  KPhi * [1 + d*cos(n*Phi)]
                    #  with trans = 180
                    #
                    # Again for ethane, d=+1 and at Phi=180, E is min.
                    #
                    # Phi0 = 0   ==> d=+1
                    # Phi0 = 180 ==> d=-1

                    if float(Phi0) == 0.0:
                        d = '-1'
                    elif float(Phi0) == 180.0:
                        d = '+1'
                    else:
                        raise RuntimeError(
                            'LAMMPS cannot handle Phi0 = {}'.format(Phi0)
                        )

                    lines.append(
                        '{:6d} harmonic {} {} {}'.format(counter, KPhi, d, n) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                elif form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {} {} {} {}'.format(
                            counter, values['V1'], values['Phi0_1'],
                            values['V2'], values['Phi0_2'], values['V3'],
                            values['Phi0_3']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

            # middle bond-torsion_3 coefficients, which must match torsions
            # in order & number
            lines.append('')
            lines.append('MiddleBondTorsion Coeffs')
            lines.append('')
            for counter, parameters, torsions in zip(
                range(1, eex['n_middle_bond-torsion_3_types'] + 1),
                eex['middle_bond-torsion_3 parameters'],
                eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                torsion_form = torsions[0]
                if torsion_form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {} {}'.format(
                            counter, values['V1'], values['V2'], values['V3'],
                            values['R0']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

            # end bond-torsion_3 coefficients, which must match torsions
            # in order & number
            lines.append('')
            lines.append('EndBondTorsion Coeffs')
            lines.append('')
            for counter, parameters, torsions in zip(
                range(1, eex['n_end_bond-torsion_3_types'] + 1),
                eex['end_bond-torsion_3 parameters'], eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                torsion_form = torsions[0]
                if torsion_form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {} {} {} {} {} {}'.format(
                            counter, values['V1_L'], values['V2_L'],
                            values['V3_L'], values['V1_R'], values['V2_R'],
                            values['V3_R'], values['R0_L'], values['R0_R']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

            # angle-torsion_3 coefficients, which must match torsions
            # in order & number
            lines.append('')
            lines.append('AngleTorsion Coeffs')
            lines.append('')
            for counter, parameters, torsions in zip(
                range(1, eex['n_angle-torsion_3_types'] + 1),
                eex['angle-torsion_3 parameters'], eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                torsion_form = torsions[0]
                if torsion_form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {} {} {} {} {} {}'.format(
                            counter, values['V1_L'], values['V2_L'],
                            values['V3_L'], values['V1_R'], values['V2_R'],
                            values['V3_R'], values['Theta0_L'],
                            values['Theta0_R']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

            # angle-angle-torsion_1 coefficients, which must match torsions
            # in order & number
            lines.append('')
            lines.append('AngleAngleTorsion Coeffs')
            lines.append('')
            for counter, parameters, torsions in zip(
                range(1, eex['n_angle-angle-torsion_1_types'] + 1),
                eex['angle-angle-torsion_1 parameters'],
                eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                torsion_form = torsions[0]
                if torsion_form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {}'.format(
                            counter, values['K'], values['Theta0_L'],
                            values['Theta0_R']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

            # bond-bond_1_3 coefficients, which must match torsions
            # in order & number
            lines.append('')
            lines.append('BondBond13 Coeffs')
            lines.append('')
            for counter, parameters, torsions in zip(
                range(1, eex['n_bond-bond_1_3_types'] + 1),
                eex['bond-bond_1_3 parameters'], eex['torsion parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                torsion_form = torsions[0]
                if torsion_form == 'torsion_3':
                    lines.append(
                        '{:6d} class2 {} {} {}'.format(
                            counter, values['K'], values['R10'], values['R30']
                        ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )
                else:
                    lines.append(
                        '{:6d} skip'.format(counter) +
                        ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                            types[0], types[1], types[2], types[3],
                            real_types[0], real_types[1], real_types[2],
                            real_types[3]
                        )
                    )

        # out-of-planes
        if eex['n_oops'] > 0:
            lines.append('')
            lines.append('Impropers')
            lines.append('')
            for counter, tmp in zip(range(1, eex['n_oops'] + 1), eex['oops']):
                i, j, k, l, index = tmp
                lines.append(
                    '{:6d} {:6d} {:6d} {:6d} {:6d} {:6d}'.format(
                        counter, index, i, j, k, l
                    )
                )

            lines.append('')
            lines.append('Improper Coeffs')
            lines.append('')
            for counter, parameters in zip(
                range(1, eex['n_oop_types'] + 1), eex['oop parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                lines.append(
                    '{:6d} {} {}'.format(counter, values['K'], values['Chi0'])
                    + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                        types[0], types[1], types[2], types[3], real_types[0],
                        real_types[1], real_types[2], real_types[3]
                    )
                )

            # angle-angle
            lines.append('')
            lines.append('AngleAngle Coeffs')
            lines.append('')
            for counter, parameters in zip(
                range(1, eex['n_angle-angle_types'] + 1),
                eex['angle-angle parameters']
            ):
                form, values, types, parameters_type, real_types = \
                    parameters
                lines.append(
                    '{:6d} {} {} {} {} {} {}'.format(
                        counter, values['K1'], values['K2'], values['K3'],
                        values['Theta10'], values['Theta20'], values['Theta30']
                    ) + ' # {}-{}-{}-{} --> {}-{}-{}-{}'.format(
                        types[0], types[1], types[2], types[3], real_types[0],
                        real_types[1], real_types[2], real_types[3]
                    )
                )

        lines.append('')
        return lines

    def to_lammps_units(self, value):
        dimensionality = str(value.dimensionality)
        return value.to(lammps_units[self.lammps_units][dimensionality])

    def magnitude_in_lammps_units(self, value):
        if isinstance(value, units_class):
            return self.to_lammps_units(value).magnitude
        else:
            return value

    def analyze(self, indent='', **kwargs):
        """Analyze the output of the calculation
        """
        # Get the first real node
        node = self.subflowchart.get_node('1').next()

        while node is not None:
            for value in node.description:
                printer.important(value)
                printer.important(' ')

            # Find any trajectory files
            id = '_'.join(str(e) for e in node._id)

            filenames = glob.glob(
                os.path.join(self.directory, '*trajectory*' + id + '.txt')
            )

            for filename in filenames:
                data = self.analyze_trajectory(filename)
                node.analyze(data=data)

            node = node.next()

        return

    def analyze_trajectory(self, filename, sampling_rate=20):
        """Read a trajectory file and do the statistical analysis
        """
        import seamm_util.md_statistics as md_statistics

        results = {}

        # Process the trajectory data
        with open(filename, 'r') as fd:
            data = pandas.read_csv(
                fd,
                sep=' ',
                header=0,
                comment='#',
                index_col=1,
            )

        logger.debug('Columns: {}'.format(data.columns))
        logger.debug('  Types:\n{}'.format(data.dtypes))

        printer.normal(
            '       Analysis of ' + os.path.basename(filename) + '\n'
        )

        printer.normal(
            '               Property           Value       stderr    tau   '
            ' ineff\n'
            '          --------------------   ---------   ------- -------- '
            ' ------'
        )
        correlation = {}
        summary_file = os.path.splitext(filename)[0] + '.summary'
        with open(summary_file, 'w') as fd:
            x = data.index
            for column in data.columns[1:]:
                y = data[column]

                # Find the autocorrelation time...
                t_delta = x[1] - x[0]
                result = md_statistics.analyze_autocorrelation(
                    y, method='zr', nlags=16, interval=t_delta
                )
                correlation[column] = result

                for key, value in result.items():
                    if 'acf' not in key and 'confidence' not in key:
                        results['{},{}'.format(column, key)] = value

                # And get the statistics accounting for the correlation
                n_step = int(round(result['inefficiency']))

                x0 = statsmodels.tools.add_constant(data.index[::n_step])
                y0 = data[column][::n_step]
                model = statsmodels.api.OLS(y0, x0)
                fit = model.fit()

                results[column] = fit.params['const']

                # Convert warnings to errors, for statsmodels.
                with warnings.catch_warnings():
                    warnings.filterwarnings('error')
                    try:
                        bse = fit.bse['const']
                    except Exception:
                        bse = float('Inf')
                    results['{},stderr'.format(column)] = bse

                fd.write(
                    'Summary of statistics for {} n_step = {}\n'.format(
                        column, n_step
                    )
                )

                # Convert warnings to errors, for statsmodels.
                with warnings.catch_warnings():
                    warnings.filterwarnings('error')
                    try:
                        fd.write('{}\n\n'.format(fit.summary()))
                    except Exception as e:
                        fd.write('{}\n\n'.format(str(e)))

                printer.normal(
                    __(
                        '{column:>23s} = {value:9.3f} ± {stderr:7.3f}'
                        ' {tau:8.1f} {inefficiency:7.1f}',
                        column=column,
                        value=fit.params['const'],
                        stderr=bse,
                        **result,
                        indent=7 * ' ',
                        wrap=False,
                        dedent=False
                    )
                )

                if False:
                    result = statsmodels.tsa.stattools.adfuller(y0)
                    print(
                        '\n\t   Testing Convergence with Augmented '
                        'Dickey-Fuller method',
                        file=fd
                    )
                    print('\tADF Statistic: %f' % result[0], file=fd)
                    print('\tp-value: %f' % result[1], file=fd)
                    print('\tCritical Values:', file=fd)
                    for key, value in result[4].items():
                        print('\t\t%2s: %.3f' % (key, value), file=fd)
                    print('\n\n\n', file=fd)

        # Create graphs of the property

        pdf_file = os.path.splitext(filename)[0] + '.pdf'
        with PdfPages(pdf_file) as pdf:
            for column in data.columns[1:]:
                inefficiency = correlation[column]['inefficiency']
                n_step = int(round(inefficiency))
                n_c = correlation[column]['n_c']

                lags = 3 * n_c
                if lags > len(data) / 2:
                    lags = int(len(data) / 2)

                if lags > 1:
                    x = data.index[::n_step]
                    y = data[column][::n_step]

                    figure = pyplot.figure(figsize=(7, 9.5))
                    figure.subplots_adjust(hspace=0.4, wspace=0.4)
                    figure.suptitle('Analysis of ' + column)
                    ax1 = figure.add_subplot(
                        211,
                        title='Trajectory',
                        xlabel='time (fs)',
                        ylabel=LAMMPS.display_units[column]
                    )
                    ax1.plot(x, y)

                    ax2 = figure.add_subplot(212)
                    plot_acf(
                        data[column],
                        ax=ax2,
                        lags=lags,
                        use_vlines=False,
                        linestyle='-',
                        marker=""
                    )

                    pdf.savefig(figure)
                    pyplot.close()

            d = pdf.infodict()
            d['Title'] = 'LAMMPS Trajectory Analysis'
            d['Author'] = 'MolSSI Framework'
            d['Subject'] = 'Analysis of LAMMPS trajectories'
            d['Keywords'] = 'LAMMPS dynamics'
            d['CreationDate'] = datetime.datetime.today()
            d['ModDate'] = datetime.datetime.today()

        return results
