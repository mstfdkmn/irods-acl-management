# irods-acl-admin

## Summary
This is a complementary command line utility for rodsadmin users to manage permissions - ACLs - in iRODS easily. Those commands can be used in case `ils` and `ichmod` of `iCommands` don't meet what you need.

## How to use
A set of scripts available in the `commands` directory can be used mainly for copying ACLs from one path (an absolute iRODS collection or data object path) to another and for comparing available ACLs on two collections. Those commands can also be used for facilating some other permission related operations. Each command will show a documentation that describes funcinalities, arguments and examples by `-h` or `--help` e.g. `iacl-copy --help`. 

- `iacl-add` can be used to add and remove a specified permission to/from an iRODS path for a user or group.

``` bash
iacl-add -u userBob -o read -p /tempZone/home/rods/data_obj.txt
```

- `iacl-clear` can be used to remove all existing permissions from an iRODS path. If it is used with the `-r` option for a collection path, then it removes all permissions recursively.

``` bash
iacl-clear -p /tempZone/home/rods/data.txt
```

- `iacl-compare` is used for listing permissions of two paths for the sake of comparison.

``` bash
iacl-compare -sr /tempZone/home/rods/coll_A -tr /tempZone/home/bob/coll_B
```

- `iacl-copy` can copy permissions from one iRODS path to another.

``` bash
iacl-copy -sp /tempZone/home/bob/collection_A /tempZone/home/rods/data_obj.txt
```

- `iacl-inherit` is used for setting inherit or removing it. It accepts not only `inherit` or `noninherit` but also different boolean expressions (yes/no, true/false) as arguments.

``` bash
iacl-inherit -i true -c /tempZone/home/rods/collection_A
```

- `iacl-list` can be used to list the granted permissions. The aim of this command is to offer different options for various scenarios.

``` bash
iacl-list -r /tempZone/home/rods
```

`PermissionManager` can also be used in any script by importing it as long as authentication to iRODS is ensured.

## Dependencies

- Python3
- python-irodsclient

## Installation

- Clone or download from Gitea/GitHub
- Set the `$iRODS_ACL_ROOT` environment variable to the location of
  irods-acl-admin's root directory
- Add the `$iRODS_ACL_ROOT` directory to your `$PYTHONPATH`
- Add the `$iRODS_ACL_ROOT/commands` directory to your `$PATH`