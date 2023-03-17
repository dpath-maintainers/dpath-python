import os
from setuptools import setup

import dpath.version

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

if __name__ == "__main__":
    setup(
        name="dpath",
        url="https://github.com/dpath-maintainers/dpath-python",
        version=dpath.version.VERSION,
        description="Filesystem-like pathing and searching for dictionaries",
        long_description=long_description,
        author=("Caleb Case, "
                "Andrew Kesterson"),
        author_email="calebcase@gmail.com, andrew@aklabs.net",
        license="MIT",
        install_requires=[],
        scripts=[],
        packages=["dpath"],
        data_files=[],
        package_data={"dpath": ["py.typed"]},

        # Type hints are great.
        # Function annotations were added in Python 3.0.
        # Typing module was added in Python 3.5.
        # Variable annotations were added in Python 3.6.
        # Python versions that are >=3.6 are more popular.
        #   (Source: https://github.com/hugovk/pypi-tools/blob/master/README.md)
        #
        # Conclusion: In order to accommodate type hinting support must be limited to Python versions >=3.6.
        # 3.6 was dropped because of EOL and this issue: https://github.com/actions/setup-python/issues/544
        python_requires=">=3.7",
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Typing :: Typed',
        ],
    )
