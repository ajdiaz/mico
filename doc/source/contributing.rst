============
Contributing
============

For more information, please see the official contribution docs at
http://mico.ajdiaz.me/en/latest/contributing.html.


Contributing Code
=================

* A good patch:

  * is clear.
  * works across all supported versions of Python.
  * follows the existing style of the code base (PEP-8).
  * has comments included as needed.

* A test case that demonstrates the previous flaw that now passes
  with the included patch.
* If it adds/changes a public API, it must also include documentation
  for those changes.
* Must be appropriately licensed (GPLv2 or newer version).


Reporting An Issue/Feature
==========================

* Check to see if there's an existing issue/pull request for the
  bug/feature. All issues are at https://github.com/ajdiaz/mico/issues
  and pull reqs are at https://github.com/ajdiaz/mico/pulls.
* If there isn't an existing issue there, please file an issue. The ideal
  report includes:

  * A description of the problem/suggestion.
  * How to recreate the bug.
  * If relevant, including the versions of your:

    * Python interpreter
    * mico
    * Optionally of the other dependencies involved

  * If possile, create a pull request with a (failing) test case demonstrating
    what's wrong. This makes the process for fixing bugs quicker & gets issues
    resolved sooner.

What we need?
=============

* To improve mico we need a lot of *new libraries*, core libraries is our main
  focus right now, for next versions of mic we like to have a lot of core
  libs, such like change parameters in the OS, modify some base system
  config, or more high level ones like "Install a full LAMP architecture".
  Every new library is welcome.

* We need more pre-defined templates, like "ls" does. For example a cost
  template to calculate EC2 budget.

* More EC2 libraries, for example for S3.

* Fix bugs... we need to remove the Beta tag ;)


