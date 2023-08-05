# OXO

**oxo_pkg ported for python 2.7**

A naughts & crosses game 

##### *note: requires python version >= 2.7*

# Install

To install run command:

`python -m pip install --user --upgrade oxo_2_pkg`

if installing from [TestPyPi](https://test.pypi.org/project/oxo-pkg/) run:

`python -m pip install --user --index-url https://test.pypi.org/simple/ oxo_2_pkg`

# Run

oxo can either by ran as a commandline script or as a python package ran in the Python REPL.

#### - Run in python REPL :

Open the python REPL

`python`

import and run the package

\>`import oxo_2_pkg`

\>`oxo_2_pkg.run()`

#### - Run in commandline :

run `oxo-2` in a commandline terminal.

#### run locally :

run `python ./oxo-2` from project home directory.

### options

See below text:

```text
here is a list of accepted arguments: 
    --hard     :  activates hard-mode
    --s-hard   :  activates super-hard-mode
    --version  :  show current version number
    --help     :  show help options
```

To see these at any point run `oxo-2 --help`

#### troubleshooting

try `which oxo-2`

This should print something like `/Users/your.username/Library/Python/2.7/bin/oxo-2`

If not find the equivalent location in your filesystem (where pip installs applications to), check that `oxo-2` binary file is present, & add the location to your PATH.

# Tests

from project home directory run

`python -m unittest test.test_methods.TestMethods`

# Build

`python3 -m pip install --user --upgrade setuptools wheel` (install / update wheel & setuptools)

`python3 setup.py sdist bdist_wheel`

Produces a .whl built distribution & a tar file of the source code in `dist/` directory.

To install the locally built version run `python -m pip install --user --upgrade dist/*`

# Release

Increment release number in `oxo_2_pkg/resources/version.md` file.

Make sure the latest version is built with above build step.

Upload the build with [twine](https://pypi.org/project/twine/): 

`python3 -m pip install --user --upgrade twine` (install / update twine)

`python3 -m twine upload dist/*` 

To upload to [TestPyPi](https://test.pypi.org/project/oxo-pkg/) run:

`python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*` 

*Note: it currently seems best to build & upload using python3*
