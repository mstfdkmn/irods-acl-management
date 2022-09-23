import os
import os.path
import ssl
from irods.session import iRODSSession


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