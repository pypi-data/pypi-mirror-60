# miniga4py #
Minimal Python bindings for the Global Arrays Toolkit Library.
Implements a *subset* of the [ga4py](https://github.com/GlobalArrays/ga4py)
Python library.

## Provides miniga4py ##
the Python package that allows the usage of the Global Arrays Toolkit
Library from Python3.

It has been developed to be used in
[LARGE](https://bitbucket.org/ncreati/large)

# NOTE: #
Install [numpy](https://pypi.org/project/numpy),
[mpi4py](https://pypi.org/project/mpi4py) and
[globalarrays](https://pypi.org/project/globalarrays) **before**
installing miniga4py!

### Install the package ###
	pip3 install miniga4py

Or download the whole repository:

	git clone https://bitbucket.org/bvidmar/miniga4py

and then

    cd miniga4py

and install as preferred:

* python3 setup.py install
* pip3 install

### Check the installation ###
	mpiexec -n 4 testminiga4py

### The Author ###
* [Roberto Vidmar](mailto://rvidmar@inogs.it)

### The Mantainers ###
* [Roberto Vidmar](mailto://rvidmar@inogs.it)
* [Nicola Creati](mailto://ncreati@inogs.it)
