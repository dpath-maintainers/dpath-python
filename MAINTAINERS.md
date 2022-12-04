Who Maintains DPATH
===================

dpath was created by and originally maintained by Andrew Kesterson <andrew@aklabs.net> and Caleb Case <calebcase@gmail.com>. In July
of 2020 they put out a call for new maintainers. [@bigsablept](https://github.com/bigsablept) and 
[@moomoohk](https://github.com/moomoohk) stepped up to become the new maintainers.

There are several individuals in the community who have taken an active role in helping to maintain the project and submit fixes. Those individuals are shown in the git changelog.

Where and How do we communicate
===============================

The dpath maintainers communicate in 3 primary ways:

1. Email, directly to each other.
2. Github via issue and pull request comments
3. A monthly maintainers meeting via Zoom

The remainder of this document is subject to change after further discussion among the new maintainers.

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

Branching Strategy
==================

We run a clean bleeding edge master. Long term support for major version numbers are broken out into version branches.

* master : Current 3.x (bleeding edge) development
* version/1.x : 1.x series bugfixes
* version/2.x : 2.x series features and bugfixes

We name bugfixes as "bugfix/ISSUENUMBER_shortname"; features are named "feature/ISSUENUMBER_shortname". All branches representing work against an issue must have the issue number in the branch name.

Cutting a New Release
=====================

Releases for dpath occur automatically from Github Actions based on version changes on the master branch.

Due to legacy reasons older tag names do not follow a uniform format:

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

Moving forward version numbers and tag names will be identical and follow the standard semver format.

The version string is stored in `dpath/version.py` and tag names/release versions are generated using this string.

    akesterson@akesterson:~/dpath-python$ cat dpath/version.py
    VERSION = "2.0.0"

To cut a new release, follow this procedure:

1. Commit a new `dpath/version.py` on the appropriate branch with the format "MAJOR.MINOR.RELEASE".
2. Github Actions SHOULD push the new release to PyPI on merge to `master`.

See `.github/workflows/deploy.yml` for more information.

If the Github workflow fails to update pypi, follow the instructions on manually creating a release, here:

https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives

Deployment CI was previously implemented using [Travis CI](https://travis-ci.org/github/akesterson/dpath-python).

Running Tests
=============

Tests are managed using [tox](https://tox.readthedocs.io/en/latest/).

Environment creation and dependency installation is managed by this tool, all one has to do is install it with `pip` and run `tox` in this repo's root directory.

Tests can also be run with Github Actions via the [tests.yml](https://github.com/dpath-maintainers/dpath-python/actions/workflows/tests.yml) workflow.

This workflow will run automatically on pretty much any commit to any branch of this repo but manual runs are also available.
