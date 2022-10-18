import os
import os.path
import ssl
import csv
import json
from datetime import datetime
from irods.session import iRODSSession
from irods.models import Collection, DataObject, UserGroup, User
from irods.column import Criterion
from irods.query import SpecificQuery


class GetiRODSSession(iRODSSession):
    """
    GetiRODSSession class is used to get an easy session
    by using the iRODSSession class from python-irodsclient.
    Example:
    with GetiRODSSession() as session:
        pass
    """

    def __init__(self):
        try:
            env_file = os.environ['IRODS_ENVIRONMENT_FILE']
        except KeyError:
            env_file = os.path.expanduser('~/.irods/irods_environment.json')
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
        ssl_settings = {'ssl_context': ssl_context}
        iRODSSession.__init__(self, irods_env_file=env_file, **ssl_settings)


def query_data_obj(session, coll_path):
    """
    A generator function:
    It queries data object name and collection name
    based on collection name criteria.
    Parameters
    ----------
    session : object
        an iRODS session object
    coll_path : str
        iRODS collection path
    Returns
    -------
    A generator object for iRODS data object path
    """
    
    query = session.query(DataObject.name, Collection.name).filter(
                               Collection.name == coll_path)            
    for result in query:
        data_obj_path = "{}/{}".format(
                        result[Collection.name], result[DataObject.name])
        yield data_obj_path

def check_user_group(session, user):
    """
    A function to know the gorup user type:
    Parameters
    ----------
    session : object
        an iRODS session object
    user : str
        a user/group in iRODS
    Returns
    -------
    True/False
    """

    result = session.query(UserGroup).filter(
    Criterion('=', User.type, 'rodsgroup')).filter(
    Criterion('=', User.name, user))

    return len(result.all().rows) > 0

def get_objects_with_no_acl(session, collection_path):
    """
    A function to get the objects that don't have any permission on.
    Parameters
    ----------
    session : object
        an iRODS session object
    collection_path : str
        an absolute in iRODS
    Returns
    -------
    object_list_with_no_acl : dict
    """

    collection = session.collections.get(collection_path)
    object_list_with_no_acl = dict()
    object_list_with_no_acl.setdefault('coll', [])
    object_list_with_no_acl.setdefault('data_obj', [])
    all_colls = collection.walk()
    for coll in all_colls:
        coll_path = coll[0].path
        coll_instance = session.collections.get(coll_path)
        permissions_collections = session.permissions.get(coll_instance)
        if len(permissions_collections) == 0:
            object_list_with_no_acl['coll'].extend([coll_path])
        for obj in coll[0].data_objects:
            obj_path = obj.path
            obj_instance = session.data_objects.get(obj_path)
            permissions_data_objects = session.permissions.get(obj_instance)
            if len(permissions_data_objects) == 0:
                object_list_with_no_acl['data_obj'].extend([obj_path])
    return object_list_with_no_acl

def get_objects_with_no_acl_for_entire_zone(session):
    """
    A function to get the objects that don't have any
    permission on in the entire zone.
    Parameters
    ----------
    session : object
        an iRODS session object
    Returns
    -------
    object_list_with_no_acl : list
    """

    object_list_with_no_acl = []
    sql_obj = 'select data_id, data_name from R_DATA_MAIN where data_id not in \
                (select object_id from R_OBJT_ACCESS)'
    alias_obj = 'list_orphaned_data_object'
    columns_obj = [DataObject.id, DataObject.name]
    sql_coll = 'select coll_id, coll_name from R_COLL_MAIN where coll_id not in \
                (select object_id from R_OBJT_ACCESS)'
    alias_coll = 'list_orphaned_collections'
    columns_coll = [Collection.id, Collection.name]
    try:
        query_obj = SpecificQuery(session, sql_obj, alias_obj, columns_obj)
        query_coll = SpecificQuery(session, sql_coll, alias_coll, columns_coll)
    except Exception as err:
        print(err)
    else:
        query_obj.register()
        query_coll.register()
        try:
            for result in query_obj:
                query = session.query(Collection.name, DataObject.name).filter(
                        Criterion('=', DataObject.name, result[DataObject.name]))
                object_list_with_no_acl.append(('data_obj', [f'{i[Collection.name]}/{i[DataObject.name]}' \
                                                for i in query][0]))
            for result in query_coll:
                object_list_with_no_acl.append(('collection', result[Collection.name]))
        except Exception as err:
            print(err.args)
    finally:
        query_obj.remove()
        query_coll.remove()
    return object_list_with_no_acl

def write_acl_csv(session, coll_path, local_path):
    """
    A function to write ACLs of a given collection to a csv file.
    ----------
    session : object
        an iRODS session object
    collection_path : str
        an absolute in iRODS
    local_path : str
        an absolute local file system path
    """

    collection = session.collections.get(coll_path)
    all_colls = collection.walk()
    filename = f"{local_path}/{'irods_permissions_{0}.csv'.format(datetime.today().strftime('%Y%m%d_%H%M'))}"
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(['iRODS PATH', 'USER NAME', 'ACL'])
        for coll in all_colls:
            coll_path = coll[0].path
            coll_instance = session.collections.get(coll_path)
            permissions_collections = session.permissions.get(coll_instance)
            writer.writerows([(item.path, item.user_name, item.access_name) for item in permissions_collections])
            for obj in coll[0].data_objects:
                obj_path = obj.path
                obj_instance = session.data_objects.get(obj_path)
                permissions_data_objects = session.permissions.get(obj_instance)
                writer.writerows([(item.path, item.user_name, item.access_name) for item in permissions_data_objects])

def write_acl_json(session, coll_path, local_path):
    """
    A function to write ACLs of a given collection to a json file.
    ----------
    session : object
        an iRODS session object
    collection_path : str
        an absolute in iRODS
    local_path : str
        an absolute local file system path
    """

    filename = f"{local_path}/{'irods_permissions_{0}.json'.format(datetime.today().strftime('%Y%m%d_%H%M'))}"
    collection = session.collections.get(coll_path)
    all_colls = collection.walk()
    acl_dict = dict()
    for coll in all_colls:
        single_coll_path = coll[0].path
        coll_instance = session.collections.get(single_coll_path)
        permissions_collections = session.permissions.get(coll_instance)
        for item in permissions_collections:
            acl_dict[item.path] = {}
            break
        [acl_dict[item.path].update({item.user_name: item.access_name}) for item in permissions_collections]

        for obj in coll[0].data_objects:
            obj_path = f'{coll[0].path}/{obj.name}'
            obj_instance = session.data_objects.get(obj_path)
            permissions_data_objects = session.permissions.get(obj_instance)
            for item in permissions_data_objects:
                acl_dict[item.path] = {}
                break
            [acl_dict[item.path].update({item.user_name: item.access_name}) for item in permissions_data_objects]
    with open(filename, 'a') as write_file:
            json.dump(acl_dict, write_file, indent=True)