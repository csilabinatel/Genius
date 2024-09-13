#!/bin/bash

acronim_project=$1
url_project=$2

# remove git tracking
rm -rf .git

# update gitignore for untrack folders
echo "dataset/" >> .gitignore
# echo "docs/" >> .gitignore
echo "notebooks/" >> .gitignore
# echo "scripts/" >> .gitignore

# update acronim name for files 
sed -i "s/pdia/$acronim_project/g" scripts/pdia_git_commit.sh
find . -name "*pdia*" | sed -e "p;s/pdia/$acronim_project/" | xargs -n2 mv


# delete mock files
find -type f -name "mock.txt" -delete

# clean readme file 
: > README.md

# set new repository track
git init
git add --all
git commit -m "Initial Commit"
git remote add origin $url_project
git push -u origin HEAD:master
