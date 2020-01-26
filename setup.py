from distutils.core import setup
import dpath.version
import os


long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

if __name__ == "__main__":
    setup(
        name="dpath",
        url="https://www.github.com/akesterson/dpath-python",
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
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
