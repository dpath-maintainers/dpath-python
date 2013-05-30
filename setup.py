from distutils.core import setup
import dpath.version
import os
import sys

if __name__ == "__main__":
    setup(
        name="dpath",
        url="https://www.github.com/akesterson/dpath-python",
        version=dpath.version.VERSION,
        description="Filesystem-like pathing and searching for dictionaries",
        long_description="""
DPath is a library that allows you to access dictionaries similar to using find over a filesystem. The proper documentation is maintained on GitHub: https://github.com/akesterson/dpath-python

Version 1.2 introduces a number of fixes against 1.1:

    * List handling has been completely redone. Various builds of 1.1 had fundamentally broken list handling. 1.2 handles list insertions, deletions, and searches as expected.

    * The backend path library has been improved to include type information with each path component, so the issue of lists mysteriously being transformed into dictionaries will no longer happen

    * The merge function's filtering has been fixed; before, it was broken, as directory nodes were merged in before filtering leaf nodes, making the filters essentially useless.

    * The unit test suite has been expanded.
""",
        author=("Caleb Case, "
                "Andrew Kesterson"),
        author_email="calebcase@gmail.com, andrew@aklabs.net",
        license="MIT",
        install_requires=[],
        scripts=[],
        packages=["dpath"],
        data_files=[],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

