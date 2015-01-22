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
"""warn about smelly changes in added code before allowing a commit

When "smelly" changes would be committed, they will be printed out and you
will be prompted whether to actually do the commit.
"""

import os
import re
import sys
import fnmatch

# reopen standard input
sys.stdin = open('/dev/tty', 'r')

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

# the master dict maps glob patterns to a list of smelly patterns
SMELLY_STUFF = {
    '*.js': [debugger_stmt],
    '*.py': [print_stmt, zero_div, set_trace, bare_raise, traceback_print],
    '*': [vim_cmd, merge_marker, nocommit_mark],
}

if os.name != 'nt':
    # only pick on Windows newlines if not on Windows
    SMELLY_STUFF['*'].append(windows_nl)


def write_colored(diff):
    os.popen('colordiff', 'w').write(''.join(diff))


def main():
    smelly_count = 0
    chunklines = os.popen('git diff --staged').readlines()

    indexline = 0
    hunkstart = 0
    for i, line in enumerate(chunklines):
        if line.startswith('diff'):
            indexline = i
            # new file: collect all smelly patterns for it
            filename = line.split()[-1]
            smellies = []
            for pat, smelly in SMELLY_STUFF.iteritems():
                if not fnmatch.fnmatch(filename, pat):
                    continue
                smellies.extend(smelly)
        elif line.startswith('@@'):
            hunkstart = i
        elif line.startswith('+'):
            for rex, reason in smellies:
                if rex.search(line):
                    print 'Smelly change (%s):' % reason
                    diff = chunklines[indexline:indexline+3] + \
                        chunklines[hunkstart:i+4]
                    write_colored(diff)
                    smelly_count += 1
                    break
            else:
                continue
            break

    if smelly_count:
        q = raw_input('Found %d smelly change%s. Continue (y/N)? ' %
                      (smelly_count, smelly_count != 1 and 's' or '')).lower()
        if q != 'y':
            return smelly_count
    return 0


if __name__ == '__main__':
    sys.exit(main())
