#!/bin/bash

# update requirements file
pip3 freeze > requirements.txt

# add copyright to files
./scripts/fut_add_copyright.sh

# set commit and push for remote repository
git add .
git commit -eF scripts/message.txt
git push