#!/bin/bash

for MODULE in irods json csv
do
    python -c "import $MODULE" 
    if [[ $? -eq 0 ]]
    then
        echo "The python module $MODULE is already present."
    else
        echo "You are missing the python module for $MODULE"

    fi
done


cd $HOME
echo "clone starts..."
git clone https://github.com/mstfdkmn/irods-acl-management 
echo "cloning done."