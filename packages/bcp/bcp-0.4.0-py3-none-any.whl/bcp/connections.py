"""
This module contains data structures required to connect to a database. While Auth can be instantiated on its own,
you would generally create it at the same time as the connection. Since the Auth object will contain credentials, it's
recommended to set these through secure means, such as environmental variables, so as to not accidentally check in your
credentials to your source control. Even your host name can be considered sensitive data, depending on your and your
company's policies.

Example:

.. code-block:: python

    import os
    import bcp

    host = os.environ['HOST']
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']

    conn = bcp.Connection(host, 'mssql', username, password)
    my_bcp = bcp.BCP(conn)
"""
from .exceptions import DriverNotSupportedException, InvalidCredentialException


class Auth:
    """
    This data structure collects the username and password as an authentication object.

    Args:
        username: username for the authorization
        password: password for the authorization
    """

    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        assert self.type

    @property
    def type(self) -> str:
        """
        This property identifies the authorization type depending on the username/password provided. The two options
        for authorization are Trusted and Credential. A Trusted connection is created when no username and no password
        are provided. In this case, the local user's credentials and authorization method are used. A Credential
        connection is created when both a username and a password are provided. If only one of username and password
        are provided, this raises an InvalidCredentialException.

        Returns:
            the type of connection ('Trusted' or 'Credential')
        """
        if self.username is None and self.password is None:
            return 'Trusted'
        elif self.username is not None and self.password is not None:
            return 'Credential'
        else:
            raise InvalidCredentialException

    def __repr__(self):
        return f'Auth(username={self.username}, password={len(self.password)})'


class Connection:
    """
    This data structure describes a connection to be used to instantiate a BCP instance. A host and driver must be
    supplied. A username/password combination can also be supplied upon instantiation to automatically create an
    associated Auth object. Alternatively, this can be set as an attribute after instantiation. If the username/password
    are not provided, the connection will assume a Trusted authorization in the meantime.

    Args:
        driver: the type of database (mssql, etc.)
        host: the host where the database exists
        port: the port for the database server
        username: the username for authentication
        password: the password for authentication
    """

    def __init__(self, driver: str, host: str, port: int = None, username: str = None, password: str = None):
        self.host = host
        self.port = port
        self.auth = Auth(username, password)
        self.driver = driver

    @property
    def driver(self) -> str:
        return self._driver

    @driver.setter
    def driver(self, value: str = None):
        if value not in ['mssql']:
            raise DriverNotSupportedException
        self._driver = value

    def __repr__(self):
        """
        This differs from __str__() because we don't want tracebacks to accidentally display credentials in plain text.
        """
        return f'Connection(driver={self.driver}, host={self.host}, port={self.port}, auth={repr(self.auth)})'

    def __str__(self):
        """
        This will generate a BCP formatted connection string in the dialect of the associated database.

        Returns:
             a BCP formatted, dialect-specific, connection string
        """
        if self.driver == 'mssql':
            if self.auth.type == 'Trusted':
                auth_string = f'-T'
            else:
                auth_string = f'-U {self.auth.username} -P {self.auth.password}'
            if self.port:
                machine = f'{self.host},{self.port}'
            else:
                machine = self.host
            return f'-S {machine} {auth_string}'
