Who Maintains DPATH
===================

dpath is primarily maintained by Andrew Kesterson <andrew@aklabs.net> and Caleb Case <calebcase@gmail.com>. These two individuals collectively govern the project.

There are several individuals in the community who have taken an active role in helping to maintain the project and submit fixes. Those individuals are shown in the git changelog.

Becoming a Maintainer
=====================

Nobody has to become a maintainer to submit a patch against dpath. Simply send the pull request on github.

If you would like to help triage issues, attend monthly meetings, and become a regular part of the team working on the roadmap, send an email to andrew@aklabs.net and/or calebcase@gmail.com.

Where and How do we communicate
===============================

The dpath maintainers communcate in 3 primary ways:

1. Email, directly to each other.
2. Github via issue and pull request comments
3. A monthly maintainers meeting via telephone

What is the roadmap
===================

dpath has 3 major series: 1.x, 2.x, and 3.x.

1.x is the original dpath release from way way back. It has a util library with a C-like calling convention, lots of assumptions about how it would be used (it was built originally to solve a somewhat narrow use case), and very bad unicode support.

2.x is a transitional branch that intends to fix the unicode support and to introduce some newer concepts (such as the segments library) while still being backwards compatible with 1.x.

3.x is a total reconstruction of the library that does not guarantee backwards compatibility with 1.x.

Finding and Prioritizing Work
=============================

There are GitHub project boards which show the work to be done for a given series:

https://github.com/akesterson/dpath-python/projects/

Each series has a board with 4 columns:

* Backlog. New work for this series appears here.
* To Do. This column represents work that has been prioritized and someone has agreed to do the work when they have an available time slot. Each maintainer should never have more than 1 or 2 things in To Do.
* In Progress. Maintainers are actively working on these issues.
* Done. These issues have been recently completed.

Work is prioritized depending on:

1. The type of work. Bugs almost always get worked before features.
2. The versions impacted by the work. Versions which are already in use get worked first (so 1.x before 2.x before 3.x etc)
3. The relative importance/usefulness of the work. "Really useful" tends to get worked before "nice to have".
4. The amount of time to complete the work. Quick issues tend to get worked sooner than issues that will take a long time to resolve.

There is no specific SLA around dpath, for features or bugs. However, generally speaking:

* All issues get triaged within 1 calendar month
* High priority bugs get addressed on the monthly maintainers call
* Very severe bugs are often fixed out of cycle in less than 30 days

Note that we have not always had anything remotely resembling a rigorous process around this, so there are some bugs that have lingered for several years. This is not something we intend to repeat.

Taking and Completing Work
==========================

Anyone who wants to is welcome to submit a pull request against a given issue. You do not need any special maintainer permissions to say "hey, I know how to solve that, let me send up a PR".

The more complete process goes:

1. Decide what issue(s) you will be working on
2. On the Projects tab on Github, move those items to the To Do column on the appropriate board
3. For the item you are ACTIVELY WORKING, move that item to "In Progress"
4. Create a fork of dpath-python, and name your branch for the work. We name bugfixes as "bugfix/ISSUENUMBER_shortname"; features are named "feature/ISSUENUMBER_shortname".
5. Complete and push your work on your fork. Use tox to test your work against the test suites. Features MUST ship with at least one new unit test that covers the new functionality. Bugfixes MUST ship with one new test (or an updated old test) that guards against regression.
6. Send your pull request
7. If accepted, the maintainers will merge your pull request and close the issue.


Cutting a New Release
=====================

Releases for dpath occur automatically from travis-ci based on tags on the master branch.

    akesterson@akesterson:~/dpath-python$ git tag
    1.0-0
    1.1
    1.2-66
    1.2-68
    1.2-70
    build,1.2,70
    build,1.2,71
    build,1.2,72
    build,1.3,0
    build,1.3,1
    build,1.3,2
    build,1.3,3
    build,1.4,0
    build,1.4,1
    build,1.4,3
    build,1.5,0
    build,2.0,0

Once upon a time, the version string was automatially computed based on the content of these tags. Now, however, the version string is stored statically in dpath/version.py

    akesterson@akesterson:~/dpath-python$ cat dpath/version.py
    VERSION = "2.0.0"

To cut a new release, follow this procedure:

1. Commit a new dpath/version.py on the master branch with the format "MAJOR.MINOR.RELEASE"
2. Add a new tag of the form "build,MAJOR.MINOR,RELEASE" to the master branch. This tag must have the same version number as the one commmited in dpath/version.py or we will fill your desk drawers with cockroaches.
3. Push the new master version and the associated tag to github.
4. travis-ci SHOULD push the new release to pypi.

If travis-ci fails to update pypi, follow the instructions on manually creating a release, here:

https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives