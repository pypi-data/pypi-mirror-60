# OXO

A naughts & crosses game.

##### *note: requires python version >= 3.6*

# Install

To install run command:

`python3 -m pip install --user --upgrade oxo_pkg`

if installing from [TestPyPi](https://test.pypi.org/project/oxo-pkg/) run:

`python3 -m pip install --user --index-url https://test.pypi.org/simple/ oxo_pkg`

# Run

oxo can either by ran as a commandline script or as a python package ran in the Python3 REPL.

#### - Run in python REPL :

Open the python3 REPL

`python3`

import and run the package

\>`import oxo_pkg`

\>`oxo_pkg.run()`

#### - Run in commandline :

run `oxo` in a commandline terminal.

#### run locally :

run `python3 ./oxo` from project home directory.

### options

See below text:

```text
here is a list of accepted arguments: 
    --hard     :  activates hard-mode
    --s-hard   :  activates super-hard-mode
    --version  :  show current version number
    --help     :  show help options
```

To see these at any point run `oxo --help`

#### troubleshooting

try `which oxo`

This should print something like `/Users/your.username/Library/Python/3.7/bin/oxo`

If not find the equivalent location in your filesystem (where pip installs applications to), check that `oxo` binary file is present, & add the location to your PATH.

# Tests

from project home directory run

`python3 -m unittest test.test_methods.TestMethods`

# Build

`python3 -m pip install --user --upgrade setuptools wheel` (install / update wheel & setuptools)

`python3 setup.py sdist bdist_wheel`

Produces a .whl built distribution & a tar file of the source code in `dist/` directory.

To install the locally built version run `python3 -m pip install --user --upgrade dist/*`

# Release

Increment release number in `oxo_pkg/resources/version.md` file.

Make sure the latest version is built with above build step.

Upload the build with [twine](https://pypi.org/project/twine/): 

`python3 -m pip install --user --upgrade twine` (install / update twine)

`python3 -m twine upload dist/*` 

To upload to [TestPyPi](https://test.pypi.org/project/oxo-pkg/) run:

`python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*` 