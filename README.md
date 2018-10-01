# WE@PE - Word Embeddings at Post-Editing

The WE@PE tool is used to generate Automatic Post-Editing for Automatic Machine Translation using Word Embeddings methods.

## Installation

In this section, we describe the steps to install all requirements for running the WE@PE tool.

### Installing Python3

First, make sure you have both Python3 and PyPI package manager.

``` bash
apt-get install python3 python3-pip
```

### Installing Python Tkinter

It is essencial to have Python Tkinter installed in order to run the tool GUI. This package is not available through PyPI, so one must run the following command to install it:

``` bash
apt-get install python3-tk
```

### Installing Requirements Through PyPI

The WE@PE tool uses both `numpy` and `scipy` packages, as specified on the [requirements.txt](requirements.txt) file. To install these dependencies, just run the following command:

``` bash
pip3 install -r requirements.txt
```

### Installing Apertium

To perform the morphological analysis tasks required, the [Apertium](https://www.apertium.org) tool is used, as well as `lttoolbox`. To install these, just execute the following command:

```bash
apt-get install apertium lttoolbox
```

### Installing MGIZA

The [MGIZA](https://github.com/moses-smt/mgiza) tool is used to align words from parallel corpora. This can be installed simply cloning the GitHub repository into `src/aligner/`.

## Running WE@PE

To run the tool, simply execute `src/main.py` or `python3 src/main.py`.

## Credits

This project was developed by Marcio Lima Inácio with orientation of Helena de Medeiros Caseli, from [LALIC (Laboratório de Linguística de Inteligência Computacional)](http://lalic.dc.ufscar.br/) in the Federal University of São Carlos (UFSCar).

## Acknowledgements

This work has been developed with the support from [São Paulo Research Foundation (FAPESP)](http://www.fapesp.br/), grants #2016/21317-0 (Undergraduate research grant) and #2016/13002-0 (MMeaning Project).

The opinions, hypotheses, conclusions and recommendations expressed in this material are the responsibility of the authors and do not necessarily reflect the views of FAPESP