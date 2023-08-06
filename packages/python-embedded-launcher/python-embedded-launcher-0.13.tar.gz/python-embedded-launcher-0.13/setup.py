# setup.py for python-embedded-launcher
#
# (C) 2016-2019 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import subprocess
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if 'sdist' in sys.argv[1:] or 'bdist_wheel' in sys.argv[1:]:
    # compile the launcher binaries
    # other users may need to edit the batch file or add gcc somehow to the PATH
    # sys.stdout.write(subprocess.check_output(['compile_all.bat'], cwd='src', shell=True, encoding='utf-8'))
    pass

setup(
    name="python-embedded-launcher",
    description="Launcher exe for distributing Python apps on Windows",
    version='0.13',
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="https://github.com/zsquareplusc/python-embedded-launcher",
    packages=['launcher_tool'],
    package_data={'launcher_tool': ['launcher27-32.exe', 'launcher27-64.exe',
                                    'launcher3-32.exe', 'launcher3-64.exe']},
    license="BSD",
    long_description=open('README.rst').read(),
    entry_points={
        'distutils.commands': [
            'bdist_launcher = launcher_tool.bdist_launcher:bdist_launcher'
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ],
    platforms='any',
)
