---
layout: page
title: "Installation"
category: doc
date: 2020-03-23 16:39:13
order: 1
use_math: true
---
<!-- AMiGA is covered under the GPL-3 license -->

**Table of Contents**

* TOC
{:toc}
<br />

**Note:** `AMiGA` is designed for use by scientists with different backgrounds in bioinformatics. To make `AMiGA` accessible for users with no experience in using `Python` or a command terminal,  I have added detailed instructions on how to install `AMiGA` under different computing conditions.
<br />

### [Required] Download repository or code

You can do either of the following
<br />
- Clone via the command terminal: `git clone https://github.com/firasmidani/amiga.git`
- Download manually: go to <a href="https://github.com/firasmidani/amiga">AMiGA</a>, click the green button <span style="color:#ffffff;background-color:#2ab748">&nbsp;Code&nbsp;</span> on top right corner, then click <span style="color:#075bd0;">Download ZIP</span>.

Please extract or download the ZIP folder in a location that you can easily access. You will have to point `Python` to this folder whenever you want to run `AMiGA`. You can altenatively create an alias that always points to the `amiga.py` file. 
<br /><br />

### [Required] `Python`

`Python` is a programming language that is commonly used for scientific computing.

* If you are a Max or Unix user, your machine will have `Python` pre-installed.
* If you are a Windows user and have not previously worked with `Python`, I recommend a `Python` distribution such as `Anaconda`. See this useful [guide](https://fangohr.github.io/blog/installation-of-python-spyder-numpy-sympy-scipy-pytest-matplotlib-via-anaconda.html) on installing Python.

`AMIGA` was written in `Python 3` and should be compatible with `Python>=2.7`.
<br /><br />

**Check your `Python` installation and its version**

Your machine may have multiple installations of `Python`. You should use the same installation every time you run `AMiGA`. So, it helps to know the following:

1. You can find out which Python installation you are calling with the following commands.

    `which python` in MacOS or Unix

    `where python` in Windows

2. If this is not the installation that you need, you can call a specific Python installation by pointing to its full path.

    `/Users/firasmidani/python3`  for MacOS or Unix

    `C:\Users\firasmidani\python3` for Windows

3. Make sure that you are using `Python 3`. You can identify the version of your `Python` installation with:

    `python --version`
<br /><br />

### [Optional] `Python` virtual environment

I highly recommend that you set-up a virtual `Python` environment for running `AMiGA` whether you are a new or experienced user of `Python`.  A virtual environment is a self-contained directory that will contain a copy of your `Python` installation, plus a limited number of additional packages that you select. You can create a virtual environment customized for `AMiGA` with the only packages that it needs. The main advantages are (1) you will know that your environment meets the requirements of `AMiGA` and (2) that it would not contradict the requirements of other programs that use your main `Python` installation.

Please follow these guides for creating virtual environments: a <a href="https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/">general guide</a> or a <a href="https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/">Anaconda-specific guide</a>. You can also try out my simple but limited instructions below. If the instructions below are not working for you, simply go to the before-mentioned guides and follow their more detailed instructions.
<br /><br />

**Mac OS and Unix users**

1. If you are using `Python 3.3` or newer, `venv` is a standard library and requires no additional installation. Otherwise, you can install `virtualenv`.

    `python -m pip install --user virtualenv`

2. Set-up the environment. Here, I name it `virtual_environment` and store it in my home directory.

    `python -m virtualenv /Users/firasmidani/virtual_environment`  you can substitute `venv` for `virtualenv`

3. Activate the environment. You will need to do this every time you are working with `AMiGA`.

    `source /Users/firasmidani/virtual_environment/bin/activate`

<br />
**Windows Users**

1. If you are using `Python 3.3` or newer, `venv` is a standard library and requires no additional installation. Otherwise, you can install `virtualenv`.

    `python -m pip install --user virtualenv`

2. Set-up the environment. Here, I name it `virtual_environment` and store it in my home directory.

    `python -m virtualenv C:\Users\firasmidani\virtual_environment`  you can substitute `venv` for `virtualenv`

3. Activate the environment. You will need to do this every time you are working with `AMiGA`.

    `C:\Users\firasmidani\virtual_environment\Scripts\activate`

<br />
**Anaconda users**

1. Set-up the environment.Here, I name it `virtual_environment`.

    `conda create -n virtual_environment`

2. Activate the environment. You will need to do this every time you are working with `AMiGA`.

    `conda activate virtual_environment`  for `Anaconda` version 4.6 or newer

<br />

### [Required] `Python` package requirements

Please follow these instructions to install all requirements. See `amiga/requirements.txt` for a full list of dependencies.

- If you plan to run `AMiGA` in a virtual environment, you need to activate the environment first.

    `source /Users/firasmidani/virtual_environment/bin/activate`  example for MacOS or Unix users

- Change your directory to `AMiGA` which you cloned or downloaded from Github.

    `cd /Users/firasmidani/amiga`

- If you are using Anaconda, you can install the requirements with the following

    `conda config --add channels conda-forge`

    `conda install --file requirements.txt`

- Otherwise, you can use pip as follows:

    `pip install -r requirements.txt`

- If you are using `Anaconda` and installation of specific package(s) fails or results in an error, you can try:

    `conda config --add channels conda-forge`

    `conda install -c conda-forge PACKAGE_NAME`
