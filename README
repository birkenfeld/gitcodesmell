Git codesmell hook
==================

This hook should be used as `pre-commit`.  It checks added lines for common
"smelly" changes.  If it finds any, it will show them and prompt whether
to continue committing.

Smelly patterns that are currently recognized are:

* vim "quit" commands that leak into the file because of wrong mode
* merge conflict markers ("<<<<<<<" and ">>>>>>>")
* Windows newlines (only on non-Windows platforms)

Language-specific:

* pdb.set_trace(), in Python files
* 1/0, in Python files
* print statements, in Python files
  (I know this is going to produce false positives, but print statements
  are also the debugging tool #1 for Python)
* bare "raise" statements, in Python files
* traceback.print_* calls, in Python files
* debugger; statements inside of Javascript files

You can add more of them by editing gitcodesmell.py's SMELLY_STUFF dictionary.

This hook is copyright 2015 by Georg Brandl, and can be
distributed under the GNU GPL version 2 or later.
