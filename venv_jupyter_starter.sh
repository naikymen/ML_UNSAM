#!/bin/bash

# Setup
# sudo pacman -Syu jupyterlab jupyter-notebook

# python3 -m venv venv
# python3 -m pip install --upgrade pip
# pip install numpy scipy matplotlib pandas scikit-learn ipython ipykernel jupyter jupyterlab
# python -m ipykernel install --user --name=venv

# Source this file with "source"

source venv/bin/activate
jupyter lab &
