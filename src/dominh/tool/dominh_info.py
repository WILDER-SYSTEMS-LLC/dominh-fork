#!/usr/bin/env python3

# Copyright (c) 2020, G.A. vd. Hoorn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Retrieve basic info from controller.

Usage: dominh [--no-upload] info [options] [--short] <host>

Options:
  -h --help     Show this screen.

"""

import sys

from docopt import docopt
from requests import exceptions

import dominh


def main(argv, skip_upload=False):
    args = docopt(__doc__, argv=argv)
    try:
        c = dominh.connect(host=args['<host>'], skip_helper_upload=skip_upload)
    except (exceptions.ConnectionError, OSError) as e:
        sys.stderr.write(f"Error trying to connect to the controller: {e}\n")
        return

    if (not args['--short']):
        print('\nController info:')
        print(f'  Time                  : {c.current_time}')
        print(f'  Series                : {c.series}')
        print(f'  Application           : {c.application}')
        print(f'  Software version      : {c.system_software_version}')
        print(f'  $FNO                  : {c.variable("[*system*]$fno", typ=str).val}')

        print('\nRobot info:')

        num_groups = c.num_groups
        print(f'  Number of groups      : {num_groups}')

        for grp in [c.group(i + 1) for i in range(num_groups)]:
            print(f'  Group {grp.id}:')
            print(f'    ID                  : {grp.robot_id}')
            print(f'    Model               : {grp.robot_model}')
            print(f'    Current pose        : {grp.curpos}')

        print(f'\nGeneral override        : {c.general_override}%')

    try:
        print('\nController status:')
        print(f'  TP enabled            : {str(c.tp_enabled):5}')
        print(f'  In AUTO               : {str(c.in_auto_mode):5}')
        print(f'  In error              : {str(c.is_faulted):5}')
        print(f'  E-stopped             : {str(c.is_e_stopped):5}')
        print(f'  Remote mode           : {str(c.in_remote_mode):5}')
        print(f'  Program running       : {str(c.is_program_running):5}')
        print(f'  Program paused        : {str(c.is_program_paused):5}')
    except dominh.exceptions.DominhException as e:
        print(f"\nCouldn't access some IO: {e}")

    numregs = ', '.join([str(c.numreg(i + 1).val) for i in range(5)])

    if (not args['--short']):
        print('\nOther info:')
        print(f'\nFirst 5 numregs         : {numregs}')

        try:
            sopins = ', '.join([str(c.sopin(i + 1).val) for i in range(5)])
            print(f'\nFirst 5 SOP inputs      : {sopins}')
        except dominh.exceptions.DominhException as e:
            print(f"\nCouldn't access some IO: {e}")

        pld = c.group(1).payload(1)
        pld_frame = f'({pld.payload_x}, {pld.payload_y}, {pld.payload_z})'
        pld_inertia = f'{pld.payload_ix}, {pld.payload_iy}, {pld.payload_iz}'
        pld_final = f'{pld.payload} Kg at {pld_frame} (inertia: {pld_inertia}'
        print(
            f'\nPayload 1 in group 1    : {pld_final})'
        )

        prgs = '; '.join([f"{nam}.{ext}" for nam, ext in c.list_programs()[:5]])
        print(f'\nFirst five programs     : {prgs}')

    errs = '\n  '.join(
        [
            f'{stamp} {lvl:7s} {msg:42}'
            for _, stamp, msg, _, lvl, _ in c.list_errors()[:10]
        ]
    )
    print(f'\nTen most recent Errors:\n  {errs}')
