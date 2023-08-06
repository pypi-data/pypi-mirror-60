"""
Usage
-----
Saved queries repesent persisted SQL queries that can be
version-controlled and run directly through the API.

Example
-------
::
    from rockset import Client

    # connect securely to Rockset
    rs = Client()

    # create a saved query
    rs.SavedQuery.create('myQuery', query_sql='SELECT 1;')

    # execute a saved query
    results = rs.SavedQuery.execute('myQuery', version=1)
 
    print(results)
    
.. _SavedQuery.create:

Create a new saved query
-----------------------
Creating a saved query using the Client_ object is as simple as
calling ``rs.SavedQuery.create('myQuery', query_sql='SELECT...')``::

    from rockset import Client
    rs = Client()

    parameters = [{ 'name': 'echo', 'default_value': 'Hello, world!', 'type': 'string' }]
    query = rs.SavedQuery.create(
        name='myQuery',
        workspace='commons',
        query_sql='select :echo as echo',
        parameters=parameters
    )

.. _SavedQuery.list:

List all saved queries
--------------------
List all saved queries using the Client_ object using::

    from rockset import Client
    rs = Client()

    # List latest version of all saved queries
    queries = rs.SavedQuery.list()

    # List latest version of all saved queries in a workspace
    queries = rs.SavedQuery.list(workspace='commons')

    # List all versions of specific saved query
    collections = rs.SavedQuery.list(workspace='commons', query='myQuery')

.. _SavedQuery.retrieve:

Retrieve an existing saved query version
-------------------------------
Retrieve a saved query to run various operations on that saved query::

    from rockset import Client
    rs = Client()

    query = rs.SavedQuery.retrieve(workspace='commons', query='myQuery', version=1)

.. _SavedQuery.execute:

Execute a specific saved query version
-------------------------------
Execute a saved query to run that saved query, optionally passing in parameters::

    from rockset import Client
    rs = Client()

    parameters = [{ 'name': 'echo', 'value': 'All work and no play makes Jack a dull boy' }]
    rs.SavedQuery.execute(
        workspace='commons',
        query='myQuery',
        version=1,
        parameters=parameters
    )

.. _SavedQuery.delete:

Delete all versions of a saved query
-----------------
Use the ``delete()`` method to remove a saved query permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()

    rs.SavedQuery.delete(workspace='commons', query='myQuery')

"""
from rockset.swagger_client.api import (QueriesApi)
from rockset.swagger_client.models import (
    CreateSavedQueryRequest, UpdateSavedQueryRequest, ExecuteSavedQueryRequest
)


class SavedQueryClient(object):
    def __init__(self, client):
        self._api = QueriesApi(client)

    def create(
        self,
        name,
        workspace="commons",
        query_sql='',
        version_tag="",
        parameters=None,
        **kwargs
    ):
        request = CreateSavedQueryRequest(
            name=name,
            version_tag=version_tag,
            query_sql=query_sql,
            parameters=parameters
        )
        return self._api.create(workspace=workspace, body=request).get('data')

    def update(
        self,
        query,
        workspace="commons",
        version_tag="",
        query_sql="",
        parameters=None,
        **kwargs
    ):
        request = UpdateSavedQueryRequest(
            version_tag=version_tag, query_sql=query_sql, parameters=parameters
        )
        return self._api.update(workspace=workspace, query=query,
                                body=request).get('data')

    def list(self, **kwargs):
        workspace = kwargs.pop('workspace', None)
        query = kwargs.pop('query', None)
        if query:
            workspace = workspace if workspace else 'commons'
            # If query specified, list versions of that query
            return self._api.list_1(workspace=workspace,
                                    query=query).get('data')
        if workspace:
            # If workspace specified, list queries in that workspace
            return self._api.list_0(workspace=workspace).get('data')
        # Else list all queries in org
        return self._api.list().get('data')

    def get(self, workspace='commons', query=None, version=None, **kwargs):
        return self._api.get(workspace=workspace, query=query,
                             version=version).get('data')

    def execute(
        self,
        query=None,
        workspace='commons',
        version=None,
        parameters=None,
        **kwargs
    ):
        request = ExecuteSavedQueryRequest(parameters=parameters)
        return self._api.run(
            query=query, workspace=workspace, version=version, body=request
        )

    def delete(self, workspace='commons', query=None, **kwargs):
        return self._api.delete(workspace=workspace, query=query).get('data')

    def retrieve(self, workspace='commons', query=None, version=None, **kwargs):
        return self.get(workspace=workspace, query=query, version=version)
