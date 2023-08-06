![logo](http://1qbit.com/wp-content/uploads/2019/05/1qbitlogo.png "1QBit is awesome!")

# OpenQEMIST
[![Build Status](https://travis-ci.com/1QB-Information-Technologies/openqemist.svg?token=zt4rNJ8MTUGcpVsToGyy&branch=0.2-staging)](https://travis-ci.com/1QB-Information-Technologies/openqemist)

Harnessing the combined power of emerging quantum computing technologies and
state-of-the-art classical techniques, the Quantum-Enabled Molecular ab Initio
Simulation Toolkit, or QEMIST, is 1QBit’s innovative solution to a fundamental
and intractable problem in chemistry: ab initio simulation of molecules.

QEMIST is designed to enable the accurate calculation of molecular properties by
leveraging advanced problem decomposition (PD) techniques and quantum computing.
The variety of PD techniques implemented in QEMIST enables massively parallel
simulations by breaking down a computational chemistry task into smaller,
independent subproblems. These subproblems can use a combination of interfaces
to various classical and quantum solvers to achieve a higher level of accuracy
for large-scale, practical molecular simulations.

OpenQEMIST provides access to a portion of the functionalities of QEMIST as
open source software under an Apache 2.0 license. For more information about the
full functionality of QEMIST and to obtain additional information, please
consult our main [product page](https://1qbit.com/qemist).

## Installation
### Installation with pip
The simplest way to install the package is to use pip.

`pip install openqemist`

Before using the Microsoft Q# integration, follow the setup
[instructions](https://docs.microsoft.com/en-us/quantum/install-guide/?view=qsharp-preview)
for installing the .NET Core SDK and the Microsoft IQ# module.

### Installation from source
To install OpenQEMIST from source, simply clone the GitHub repo and add the package
to your ``PYTHONPATH``. The dependencies for running the project are the Microsoft
.NET Core SDK, IQ#, and qsharp packages as well as pyscf, numpy, and scipy. The
most current list of dependencies, as well as dependencies for building the documentation
can be found in the [Dockerfile](./docker_images/Dockerfile).

## Getting started

To get started, install the package, then see the [Jupyter notebooks](./examples/)
for example usage.

## Contents of the repository

Details the organization of this repository and the contents of each folder.

- **benchmarks** :
Long-running tests for the performance of algorithms on larger molecules

- **docker_images** :
The docker image that can be used to run the package.

- **cont_integration** :
Tools and script for continuous integration (versioning, automated testing, and updating documentation)

- **docs** :
Source code documentation and user documentation

- **examples** :
Examples and tutorials to learn how to use the different functionalities of the library

- **openqemist** :
The Python package

## Architechture of OpenQEMIST
OpenQEMIST is organized into three layers: problem decomposition, electronic
structure solvers, and hardware backends. The problem decomposition layer is
responsible for splitting the input molecule into smaller subproblems and
treating these using one particular eigenvalue solver (conceivably, fragments
could be treated using multiple solvers), then processing these results into an
overall output energy. Some electronic structure solvers use classical methods,
while others use wrappers over quantum algorithms running on quantum computing
emulators and simulators from quantum platform providers. The quantum solver
backend layer implements a common interface over libraries, emulators, and
simulators of quantum hardware.

As OpenQEMIST includes only a portion of the functionalities incorporated in QEMIST, DMET
is the only problem decomposition technique open sourced in our initial release.
This release includes the Full CI and coupled-cluster with single and double
excitations (CCSD) electronic structure solvers, as well as a quantum electronic
structure solver based on the Variational Quantum Eigensolver (VQE) algorithm.

On the hardware backend, this initial release is integrated with the Microsoft
Quantum Development Kit for running the VQE algorithm.

## Contributing
We welcome contributions to OpenQEMIST! Please open an issue or submit a pull request on GitHub to start the process.

## Citing
If you use OpenQEMIST in your research, please cite

Takeshi Yamazaki, Shunji Matsuura, Ali Narimani, Anushervon Saidmuradov, and Arman Zaribafiyan "Towards the Practical Application of Near-Term Quantum Computers in Quantum Chemistry Simulations: A Problem Decomposition Approach" Published on [arXiv](https://arxiv.org/abs/1806.01305) on Jun 4, 2018.


_Copyright 1QBit 2019. This software is released under the Apache Software License version 2.0._
