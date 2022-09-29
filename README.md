# irods-acl-management

## Summary
This is a complementary command line utility for rodsadmin users to manage permissions - ACLs - in iRODS easily. These commands listed below can be used in case `ils` and `ichmod` of `iCommands` don't meet what you need when dealing with permission releated topics. They bring mainly sort of easy solutions to the following issues:

- How to find objects that lost somehow their any available permissions (orphaned objects)?
- Who to attach permissions for those orphaned objects?
- How to copy all permissions exist on an object to another?
- How to manipulate multiple permissions (granted access) of an object at once?
- How to remove all available permissions of an object (also recursively for collections) at once?
- Can the inheritance of an collection be set with various logical notations rather than `inherit/noinherit`?
- How to list permissions of only a collection (without data object) and permissions of all sub-collections from top to down?
- Can it be possible to compare permissions of two collections (without data objects)?
- How to save output of any listed permissions in various formats (json, csv)?


## How to use
A set of scripts available in the `commands` directory can be used in any terminal - command line interface once the installation is completed correctly. Each command will show a documentation that describes funcinalities, arguments and examples by `-h` or `--help` e.g. `iacl-copy --help`. 


- iacl-copy: To copy ACLs of one object to another one.

``` bash
iacl-copy tempZone/home/bob/collection_A /tempZone/home/rods/data_obj
iacl-copy tempZone/home/bob/collection_A /tempZone/home/rods/collection_A
iacl-copy tempZone/home/bob/data_obj /tempZone/home/rods/collection_A
```

- iacl-clear: To remove all existing ACLs.

``` bash
iacl-clear /tempZone/home/rods/collection_A
iacl-clear -r /tempZone/home/group_A
iacl-clear /tempZone/home/rods/data_obj
```

- iacl-check: To control whether there is any object which does not have an ACL.

``` bash
iacl-check -r /tempZone/home/rods
iacl-check /tempZone/home/rods/collection_A
iacl-check --zone tempZone
```

- iacl-restore: To add back the ACL of originator on object which does not have an ACL.

``` bash
iacl-restore /tempZone/home/rods/data_object
iacl-restore /tempZone/home/rods/collection_A
iacl-restore -z tempZone
```

- iacl-save: To write all available ACLs of a collection structure in a `csv` or `json` file.

``` bash
iacl-save /tempZone/home/rods -l /home/user -f csv
iacl-save /tempZone/home/group_A --location /tmp --format json
```

- iacl-add: To set (add/remove/modify) permissions of an iRODS path (you can do this for multiple users at the same time).

``` bash
iacl-add read userBob userJan group_A /tempZone/home/rods/data_obj.txt
```

- iacl-inherit: To change the inheritance also with true/false and yes/no. 

``` bash
iacl-inherit true /tempZone/home/rods/collection_A
```

- iacl-list: To list only the permissions of collections when a collection is targeted, (it behaves like `ils` for data objects).

``` bash
iacl-list -r /tempZone/home/rods 
iacl-list /tempZone/home/bob
iacl-list /tempZone/home/rods/data_object
```

- iacl-compare

``` bash
iacl-compare -r /tempZone/home/rods/coll_A /tempZone/home/bob/coll_B
```

`PermissionManager` class can also be used in any script by importing it as long as authentication to iRODS is ensured.

## Dependencies

- Python3
- python-irodsclient

## Installation

- Clone or download from GitHub
- Set the `$iRODS_ACL_ROOT` environment variable to the location of
  irods-acl-admin's root directory
- Add the `$iRODS_ACL_ROOT` directory to your `$PYTHONPATH`
- Add the `$iRODS_ACL_ROOT/commands` directory to your `$PATH`

Or linux users can download `setup.sh` file and run `.setup.sh` and following commands.

``` bash
iRODS_ACL_ROOT="$HOME/irods-acl-management"
export PYTHONPATH="$PYTHONPATH:$iRODS_ACL_ROOT"
export PATH="$PATH:$iRODS_ACL_ROOT/commands"
```

## Limitations

`iacl-list -r` could be slow for the deep running because of the lack of a relevant attribute in prc for group-users.