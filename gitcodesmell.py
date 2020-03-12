#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# codesmell git hook
#
# Copyright (c) 2015 by Georg Brandl.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from __future__ import print_function

"""warn about smelly changes in added code before allowing a commit

When "smelly" changes would be committed, they will be printed out and you
will be prompted whether to actually do the commit.
"""

import os
import re
import sys
import fnmatch
import subprocess

# reopen standard input
sys.stdin = open('/dev/tty', 'r')

# ansi color escape patterns
ansi = re.compile('\x1b.*?m')

# smelly patterns are tuples (regex, reason)
nocommit_mark = (re.compile(r'XXX\(nocommit\)'), 'don\'t commit marker')
print_stmt = (re.compile(r'^\+\s*print\b'), 'print statement')
bare_raise = (re.compile(r'^\+\s*raise\s*$', re.M), 'bare raise statement')
debugger_stmt = (re.compile(r'^\+\s*debugger;'), 'javascript debugger')
zero_div = (re.compile(r'^\+\s*1/0'), 'zero division error')
set_trace = (re.compile(r'\bi?pdb\.set_trace\(\)'), 'set_trace')
traceback_print = (re.compile(r'\btraceback\.print_'), 'traceback print')
vim_cmd = (re.compile(r':(w|wq|q|x)$', re.M), 'vim exit command')
windows_nl = (re.compile(r'\r'), 'Windows newline')
merge_marker = (re.compile(r'^(>>>>>>>|<<<<<<<)'), 'merge marker')
print_macro = (re.compile(r'^\+\s*print(ln)?!\b'), 'print macro')

# the master dict maps glob patterns to a list of smelly patterns
SMELLY_STUFF = {
    '*.js': [debugger_stmt],
    '*.py': [print_stmt, zero_div, set_trace, bare_raise, traceback_print],
    '*.rs': [print_macro],
    '*': [vim_cmd, merge_marker, nocommit_mark],
}

if os.name != 'nt':
    # only pick on Windows newlines if not on Windows
    SMELLY_STUFF['*'].append(windows_nl)


def main():
    smelly_count = 0
    # we request always colored output so that we can print it nicely
    # to the console
    out, err = subprocess.Popen('git diff --staged --color=always', shell=True, stdout=subprocess.PIPE).communicate()
    if not isinstance(out, str):
        out = out.decode('latin1')
    chunklines = out.splitlines(True)

    indexline = 0
    hunkstart = 0
    for i, line in enumerate(chunklines):
        cleanline = ansi.sub('', line)
        if cleanline.startswith('diff'):
            indexline = i
            # new file: collect all smelly patterns for it
            filename = cleanline.split()[-1]
            smellies = []
            for pat, smelly in SMELLY_STUFF.items():
                if not fnmatch.fnmatch(filename, pat):
                    continue
                smellies.extend(smelly)
        elif cleanline.startswith('@@'):
            hunkstart = i
        elif cleanline.startswith('+'):
            for rex, reason in smellies:
                if rex.search(cleanline):
                    print('Smelly change (%s):\n' % reason)
                    diff = chunklines[indexline:indexline+3] + \
                        chunklines[hunkstart:i+4]
                    print(''.join(diff))
                    smelly_count += 1
                    break
            else:
                continue
            break

    if smelly_count:
        print('Found %d smelly change%s. Continue (y/N)? ' %
              (smelly_count, smelly_count != 1 and 's' or ''), end='')
        sys.stdout.flush()
        q = sys.stdin.readline().lower().strip()
        if q != 'y':
            return smelly_count
    return 0


if __name__ == '__main__':
    sys.exit(main())
