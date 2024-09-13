#!/bin/bash

venv_name=$1

# Remove venv folder git tracking
echo "$venv_name/" >> .gitignore

# Create venv
python3 -m venv $venv_name
echo "export PYTHONPATH=$PWD" >> $venv_name/bin/activate
source ./$venv_name/bin/activate
pip3 install --upgrade pip setuptools wheel
pip3 install dvc[ssh]
pip3 install -r requirements.txt
