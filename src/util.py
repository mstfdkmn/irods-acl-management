import os
import os.path
import ssl
from irods.session import iRODSSession
from irods.models import Collection, DataObject


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