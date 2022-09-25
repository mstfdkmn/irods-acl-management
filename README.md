# irods-acl-admin

## Summary
This is a complementary command line utility for rodsadmin users to manage permissions - ACLs - in iRODS easily. These commands listed below can be used in case `ils` and `ichmod` of `iCommands` don't meet what you need when dealing with permission releated topics. They bring mainly sort of easy solutions to the following issues:

- How to find objects that lost somehow their any available permissions (orphaned objects)?
- Who to attach permissions for those orphaned objects?
- How to copy all permissions exist on an object to another?
- How to manipulate multiple permissions (granted access) of an object at once?
- How to remove all available permissions of an object (also recursively for collections) at once?
- Can inheritance of an collection be set with various logical notations rather than `inherit/noinherit`?
- How to list permissions of only a collection (without data object) and permissions of all sub-collections from top to down?
- Can it be possible to compare permissions of two collections (without data objects)?
- How to save output of any listed permissions in various formats (json, csv)?


## How to use
A set of scripts available in the `commands` directory can be used in any terminal - command line interface once the installation is completed correctly. Each command will show a documentation that describes funcinalities, arguments and examples by `-h` or `--help` e.g. `iacl-copy --help`. 

- `iacl-add`

``` bash
iacl-add read userBob userJan group_A /tempZone/home/rods/data_obj.txt
```

- `iacl-clear`

``` bash
iacl-clear -r /tempZone/home/rods/collections_A
```

- `iacl-compare`

``` bash
iacl-compare -r /tempZone/home/rods/coll_A /tempZone/home/bob/coll_B
```

- `iacl-copy`

``` bash
iacl-copy tempZone/home/bob/collection_A /tempZone/home/rods/data_obj.txt
```

- `iacl-inherit`

``` bash
iacl-inherit true /tempZone/home/rods/collection_A
```

- `iacl-list`

``` bash
iacl-list -r /tempZone/home/rods /tempZone/home/bob
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

Or linux users can download `setup.sh` file and run `bash setup.sh` command.