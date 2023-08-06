"""
Workspace connection for dask-yarn

Dask-yarn does not really benefit from any sql magics. It's included here
due to being a common analytic pattern for distributed analytics using 
yarn.
"""


class Daskyarn:

    def __init__(self,kwargs,command=None):
        self.conf=kwargs
        if command is not None:
            self.command=command

    def init(self):
        from dask_yarn import YarnCluster
        from dask.distributed import Client
        if self._client is None:
            self._client = Client(YarnCluster(**self.conf))
        return(self._client)
    
    def conn(self):
        return(None)

    def qry(self,qry,r_type="df",limit=30):   
        return(None)
