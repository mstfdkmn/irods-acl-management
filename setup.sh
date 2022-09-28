#!/bin/bash

for MODULE in irods json
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
cd irods-acl-management

iRODS_ACL_ROOT=$HOME/irods-acl-management
export PYTHONPATH=$PYTHONPATH:$iRODS_ACL_ROOT
export PATH=$PATH:$iRODS_ACL_ROOT/commands