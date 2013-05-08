from distutils.core import setup
import version
import os
import sys

if __name__ == "__main__":
    setup(
        name="dpath",
        version=version.VERSION,
        description="Filesystem-like pathing and searching for dictionaries",
        long_description="dpath",
        author=("Caleb Case, "
                "Andrew Kesterson"),
        author_email="calebcase@gmail.com, andrew@aklabs.net",
        license="MIT",
        install_requires=[],
        scripts=SCRIPTS,
        packages=["dpath"],
        data_files=DATA_DIRS,
        classifiers=[
            'Development Status :: 1 - Development',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: MIT',
            'Natural Language :: English',
            'Programming Language :: Python 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

