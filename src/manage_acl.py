from irods.access import iRODSAccess
from irods.exception import CollectionDoesNotExist, DataObjectDoesNotExist
from .util import query_data_obj, check_user_group, get_objects_with_no_acl, \
                  write_acl_csv, write_acl_json, get_objects_with_no_acl_for_entire_zone


class PermissionManager(object):
    """
    This class is used to help rodsadmin users manage iRODS permissions easily
    using CLI. It copies existing ACLs from one object (data objects or collections)
    to another one. Also it can remove all given Acls on an object.
    ...
    Attributes
    ----------
    session : object
        a connection object to communicate with iRODS.
    source_path : str
        an iRODS path of which permissions(ACLs) will be copied or deleted.
    target_path : str
        an iRODS path to which permissions(ACLs) copied will be pasted.
    Methods
    -------
    __get_collection_acl():
        Based on the source path, it gets available ACLs of collections.
        Returns a list of permissions given.
    __get_data_object_acl():
        Based on the source path, it gets available ACLs of data objects.
        Returns a list of permissions given.
    copy_acl():
        Copies permissions from one object to another.
    remove_acl():
        Deletes all permissions given on an object.

    Examples:

        acl = PermissionManager(session, source_path=path)
        acl.remove_acl()
        acl = PermissionManager(session, source_path=source_path, target_path=target_path)
        acl.copy_acl()
    """

    def __init__(self, session, source_path=None, target_path=None):
        """A constructor method"""
        self.session = session
        self.target_path = target_path
        self.source_path = source_path
        if source_path is None:
            pass
        else:
            if session.collections.exists(source_path):
                self.source_path = source_path
            elif session.data_objects.exists(source_path):
                self.source_path = source_path
    
    def __get_collection_acl(self):
        """A private method to get existing ACLs on a given collection"""

        try:
            coll = self.session.collections.get(self.source_path)
            inheritance = coll.inheritance
            permissions = self.session.permissions.get(coll, report_raw_acls=True)
        except CollectionDoesNotExist:
            permissions = None
            inheritance = None
        return inheritance, permissions
        
    def __get_data_object_acl(self):
        """A private method to get existing ACLs on a given data object"""
        try:
            obj = self.session.data_objects.get(self.source_path)
            permissions = self.session.permissions.get(obj)
        except DataObjectDoesNotExist:
            permissions = None
        return permissions
    
    def copy_acl(self):
        """A method to copy existing ACLs from one iRODS path to another"""
        acls_source_collections = self.__get_collection_acl()[1]
        acls_source_data_objects = self.__get_data_object_acl()
        if acls_source_collections != None:
            for item in acls_source_collections:
                try:
                    acl_target_collections = iRODSAccess(item.access_name, self.target_path, item.user_name)                    
                    self.session.permissions.set(acl_target_collections, admin=True)
                except Exception as err:
                    print(err.code)

        if acls_source_data_objects != None:
            for item in acls_source_data_objects:
                try:
                    acl_target_data_objects = iRODSAccess(item.access_name, self.target_path, item.user_name)                    
                    self.session.permissions.set(acl_target_data_objects, admin=True)
                except Exception as err:
                    print(err.code)

    def remove_all_acl(self):
        """A method to delete existing ACLs on an iRODS path"""
        acls_source_collections = self.__get_collection_acl()[1]
        acls_source_data_objects = self.__get_data_object_acl()
        if acls_source_collections != None:
            for item in acls_source_collections:
                try:
                    acl_target_collections = iRODSAccess('null', self.source_path, item.user_name)                    
                    self.session.permissions.set(acl_target_collections, admin=True)
                except Exception as err:
                    print(err.code)

        if acls_source_data_objects != None:
            for item in acls_source_data_objects:
                try:
                    acl_target_data_objects = iRODSAccess('null', self.source_path, item.user_name)
                    self.session.permissions.set(acl_target_data_objects, admin=True)
                except Exception as err:
                    print(err.code)
    
    def remove_all_acl_recursively(self):
        """
        A method to delete existing ACLs on 
        an iRODS collection path recursively
        """
        try:
            collection = self.session.collections.get(self.target_path)
        except CollectionDoesNotExist:
            print('Recursive can only be applied on an existing collection!')
            pass
        else:
            all_colls = collection.walk()
            for item in all_colls:
                coll_path = item[0].path
                try:
                    coll = self.session.collections.get(coll_path)
                    permissions = self.session.permissions.get(coll)
                    for item in permissions:
                        acl_target_collection = iRODSAccess('null', coll_path, item.user_name)                    
                        self.session.permissions.set(acl_target_collection, admin=True)
                except Exception as err:
                    print(err.args)
                if len(coll_path) != 0:
                    result = query_data_obj(self.session, coll_path)
                    for data_path in result:
                        try:
                            obj = self.session.data_objects.get(data_path)
                            permissions = self.session.permissions.get(obj)
                        except Exception as err:
                            print(err.args)
                        for item in permissions:
                            acl_target_data_objects = iRODSAccess('null', data_path, item.user_name)
                            self.session.permissions.set(acl_target_data_objects, admin=True)

    def set_acl(self, user, alc_type, recursive=False):
        """
        A method to set (add/modify/remove) given ACLs via cli arguments to
        a user/group for an iRODS path
        """
        if recursive:
            try:
                collection = self.session.collections.get(self.target_path)
            except CollectionDoesNotExist:
                print('Recursive can only be applied on an existing collection!')
                pass
            all_colls = collection.walk()
            for item in all_colls:
                coll_path = (item[0].path)
                acl_target_collections = iRODSAccess(alc_type, coll_path, user)
                self.session.permissions.set(acl_target_collections, admin=True)
                if len(item[2]) != 0:
                    for data_obj in item[2]:
                        data_obj_name = data_obj.name
                        data_obj_path = f'{coll_path}/{data_obj_name}'
                        acl_target_data_objects = iRODSAccess(alc_type, data_obj_path, user)
                        self.session.permissions.set(acl_target_data_objects, admin=True)
        acl_target_data_path = iRODSAccess(alc_type, self.target_path, user)
        self.session.permissions.set(acl_target_data_path, admin=True)
    
    def set_inherit(self, alc_type=None):
        """
        A method to set (add/modify/remove) given ACLs via cli arguments to
        a user/group for an iRODS path
        """
        try:
            coll = self.session.collections.get(self.target_path)
        except CollectionDoesNotExist:
            print('<Inherit> can only be applied on a collection!')
            pass
        else:
            if coll:
                if alc_type == 'True' or alc_type == 'true' or alc_type == 'inherit'\
                    or alc_type == 'yes' or alc_type == 'YES':
                    acl_inherit = iRODSAccess('inherit', self.target_path)
                    self.session.permissions.set(acl_inherit,  admin=True)
                elif alc_type == 'False' or alc_type == 'false' or alc_type == 'noinherit'\
                    or alc_type == 'no' or alc_type == 'NO':
                    acl_inherit = iRODSAccess('noinherit', self.target_path)
                    self.session.permissions.set(acl_inherit, admin=True)
                else:
                    print("There's something wrong with the way your argument is typed!")
        
    def list_acl(self):
        """A method to list all given ACLs on an iRODS path"""
        inheritance, acls_source_collections = self.__get_collection_acl()
        acls_source_data_objects = self.__get_data_object_acl()
        if acls_source_collections != None:
            print(f'Inheritance: {inheritance}')
            if len(acls_source_collections) == 0:
                print('ACL - ')
            for i in acls_source_collections:
                print(f'ACL - {i.path}:')
                break
            [print(f'     g:{i.user_name}#{i.user_zone}:{i.access_name}') \
            if (check_user_group(self.session, i.user_name)) is True \
            else print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
            for i in acls_source_collections]
        if acls_source_data_objects != None:
            if len(acls_source_data_objects) == 0:
                print(f'ACL - ')
            for i in acls_source_data_objects:
                print(f'ACL - {i.path}:')
                break
            [print(f'     g:{i.user_name}#{i.user_zone}:{i.access_name}') \
            if check_user_group(self.session, i.user_name) is True \
            else print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
            for i in acls_source_data_objects]

    def list_acl_recursively(self):
        """
        A method to list all given ACLs together with inherit information
        recursively for an iRODS path
        Lists only for sub-collections from top to down
        """
        try:
            collection = self.session.collections.get(self.target_path)
        except CollectionDoesNotExist:
            print('Recursive can only be applied on a collection!')
            pass
        else:
            all_colls = collection.walk()
            for item in all_colls:
                path = item[0].path
                coll = self.session.collections.get(path)
                inheritance = coll.inheritance
                permissions = self.session.permissions.get(coll)
                print(f'Inheritance: {inheritance}')
                if len(permissions) == 0:
                    print(f'{path} \n ACL - ')
                for i in permissions:
                    print(f'ACL - {i.path}:')
                    break
                [print(f'     g:{i.user_name}#{i.user_zone}:{i.access_name}') \
                if check_user_group(self.session, i.user_name) is True \
                else print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                for i in permissions]
    
    def compare_acl_of_two_collections(self, source, target):
        """
        A method to list all given ACLs together with inherit 
        information for two iRODS paths
        Lists only for given collections and their first level data objects for comparision
        """
        try:
            collection_source = self.session.collections.get(source)
            collection_target = self.session.collections.get(target)
        except CollectionDoesNotExist:
            print('Comparision can only be applied for collections!')
            pass
        else:
            colls_source = collection_source.walk()
            for item in colls_source:
                coll_path = item[0].path
                coll = self.session.collections.get(coll_path)
                inheritance = coll.inheritance
                permissions = self.session.permissions.get(coll)
                print(f'Inheritance: {inheritance}')
                for i in permissions:
                    print(f'ACL - {i.path}:')
                    break
                [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                for i in permissions]
                for i in item[0].data_objects:
                    obj_path = f'{item[0].path}/{i.name}'
                    obj = self.session.data_objects.get(obj_path)
                    permissions_data_objects = self.session.permissions.get(obj)
                    for i in permissions_data_objects:
                        print(f'ACL - {i.path}:')
                        break
                    [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                    for i in permissions_data_objects]
                break
        
            print('\n-------------------------------TARGET COLLECTION------------------------------------\n')
            
            colls_target = collection_target.walk()
            for item in colls_target:
                coll_path = item[0].path
                coll = self.session.collections.get(coll_path)
                inheritance = coll.inheritance
                permissions = self.session.permissions.get(coll)
                print(f'Inheritance: {inheritance}')
                for i in permissions:
                    print(f'ACL - {i.path}:')
                    break
                [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                for i in permissions]
                for i in item[0].data_objects:
                    obj_path = f'{item[0].path}/{i.name}'
                    obj = self.session.data_objects.get(obj_path)
                    permissions_data_objects = self.session.permissions.get(obj)
                    for i in permissions_data_objects:
                        print(f'ACL - {i.path}:')
                        break
                    [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                    for i in permissions_data_objects]
                break

    def compare_acl_of_two_collections_recursively(self, source, target):
        """
        A method to list all given ACLs together with inherit information 
        recursively for two iRODS paths
        Lists only for sub-collections from top to down
        """
        try:
            collection_source = self.session.collections.get(source)
            collection_target = self.session.collections.get(target)
        except CollectionDoesNotExist:
            print('Recursive can only be applied on a collection!')
            pass
        else:
            colls_source = collection_source.walk()
            colls_target = collection_target.walk()
            for item in colls_source:
                path = item[0].path
                coll = self.session.collections.get(path)
                inheritance = coll.inheritance
                permissions = self.session.permissions.get(coll)
                print(f'Inheritance: {inheritance}')
                for i in permissions:
                    print(f'ACL - {i.path}:')
                    break
                [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                for i in permissions]

            print('\n-------------------------------TARGET COLLECTION------------------------------------\n')

            for item in colls_target:
                path = item[0].path
                coll = self.session.collections.get(path)
                inheritance = coll.inheritance
                permissions = self.session.permissions.get(coll)
                print(f'Inheritance: {inheritance}')
                for i in permissions:
                    print(f'ACL - {i.path}:')
                    break
                [print(f'     {i.user_name}#{i.user_zone}:{i.access_name}') \
                for i in permissions]

    def search_orphaned_objects(self, collection_path=None, data_obj_path=None, recursive=False):
        """
        A method to find the orphaned object 
        (meaning no acl exists) of a given path
        """
        if collection_path and recursive == True:
            object_list_with_no_acl = get_objects_with_no_acl(self.session, collection_path)
            if len(object_list_with_no_acl['coll']) > 0 or len(object_list_with_no_acl['data_obj']) > 0:
                print('Warning: Objects below have no granted permissions.')
                object_list_with_no_acl_list = [i for i in object_list_with_no_acl.values()]
                [print(i) for i in object_list_with_no_acl_list[0]]
                [print(i) for i in object_list_with_no_acl_list[1]]
            else:
                print('No orphaned object is available.')

        elif collection_path:
            coll_instance = self.session.collections.get(collection_path)
            permissions_collection = self.session.permissions.get(coll_instance)
            if len(permissions_collection) == 0:
                print(False)
            else:
                print('This collection has an granted permission.')

        elif data_obj_path:
            obj_instance = self.session.data_objects.get(data_obj_path)
            permissions_data_object = self.session.permissions.get(obj_instance)
            if len(permissions_data_object) == 0:
                print(False)
            else:
                print('This data object has an granted permission.')

    def search_orphaned_objects_entire_zone(self, zone_name=None):
        """
        A method to find the orphaned object 
        (meaning no acl exists) of a entire zone
        """

        object_list_with_no_acl = get_objects_with_no_acl_for_entire_zone(self.session)
        if zone_name:
            if len(object_list_with_no_acl) > 0:
                print('Warning: Objects below have no granted permissions.')
                for item in object_list_with_no_acl:
                    if item[0] == 'collection':
                        print(f'C -  {item[1]}')
                    if item[0] == 'data_obj':
                        print(item[1])
            else:
                print('There is no object that doesnt have any permission in your zone.')

    def restore_original_owner(self, collection_path=None, data_obj_path=None, zone_name=None):
        """A method to set original ACL onto the orphaned object """
        if zone_name:
            object_list_with_no_acl = get_objects_with_no_acl_for_entire_zone(self.session)
            if len(object_list_with_no_acl) > 0:
                for item in object_list_with_no_acl:
                    if item[0] == 'collection':
                        coll_instance = self.session.collections.get(item[1])
                        permissions_collection = self.session.permissions.get(coll_instance)
                        user = coll_instance.owner_name
                        acl_target_collection = iRODSAccess('own', item[1], user)
                        self.session.permissions.set(acl_target_collection, admin=True)
                    elif item[0] == 'data_obj':
                        obj_instance = self.session.data_objects.get(item[1])
                        permissions_data_object = self.session.permissions.get(obj_instance)
                        user = obj_instance.owner_name
                        acl_target_data_object = iRODSAccess('own', item[1], user)                    
                        self.session.permissions.set(acl_target_data_object, admin=True)
            else:
                print('There is no object that has missing permission to be restored in your zone.')
        elif collection_path:
            coll_instance = self.session.collections.get(collection_path)
            permissions_collection = self.session.permissions.get(coll_instance)
            if len(permissions_collection) == 0:
                user = coll_instance.owner_name
                acl_target_collection = iRODSAccess('own', collection_path, user)
                self.session.permissions.set(acl_target_collection, admin=True)
            else:
                print('This object has already a granted permission.')
        elif data_obj_path:
            obj_instance = self.session.data_objects.get(data_obj_path)
            permissions_data_object = self.session.permissions.get(obj_instance)
            if len(permissions_data_object) == 0:
                user = obj_instance.owner_name
                acl_target_data_object = iRODSAccess('own', data_obj_path, user)                    
                self.session.permissions.set(acl_target_data_object, admin=True)
            else:
                print('This object has already a granted permission.')

    def save_acl(self, coll_path, local_path, format=None):
        """
        A method to write all given ACLs of an iRODS
        path into the specified file format
        """
        if format == 'csv':
            write_acl_csv(self.session, coll_path, local_path)
        elif format == 'json':
            write_acl_json(self.session, coll_path, local_path)
        else:
            print('You did not provide a correct file format.\
                   Choose either csv or json')