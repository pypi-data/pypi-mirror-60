"""
Workspace connection for Ibis_impala

It contains a single class, Ibis_impala.
While Ibis impala presumes that the ibis user will
 be using impala with HDFS.
"""

import ibis
import pandas          as pd
from dsws.util     import pretty
from dsws.util     import sp
from dsws.util     import standard_conn_qry
from dsws.util     import no_return
from os import environ as env
from ast           import literal_eval


class Ibis_impala:

    def __init__(self,kwargs,command=None):
        """
        Workspace class from the ibis library

        Similar for other DSWS classes, the following class methods are
        provided:
         - hdfs: returns an hdfs conneciton
         - impalaClient: returns an ibis impala client 
         - qry: precesses a query, return type is dependent upon r_type requested:
            - df/raw: pandas dataframe
            - disp: pretty html form of pandas dataframe
            - msg: experimental - retuens query profile if using impala
            - cmd: standard query form to be processed. Helpful for debugging and logging
        
        Configuring an ibis class is typically done through dsws.duct, but can also be
        evaluated as:
        ```python
        from dsws.ws_ibis_impala import Ibis_impala
        kwargs = {'ibis.config':
                  {'impala.temp_db':'default',
                   'impala.temp_hdfs_path':'/usr/hive/warehouse/default'},
                  'hdfs.connect.kwargs':
                  {'host':'webhdfs.ratiocinate.com',
                   'port':14000,
                   'protocol':'webhdfs',
                   'auth_mechanism':'GSSAPI',
                   'use_https':True,
                   'verify':False},
                  'impala.connect.kwargs':
                  {'host':'impala',
                   'port':21050,
                   'database':'default',
                   'use_ssl':True,
                   'auth_mechanism':'GSSAPI'},
                  'impala.options':
                  {'request_pool':'"root.default"'}}

        ib = Ibis_impala(kwargs)
        ```
        Contrary to other common connections, Ibis for impala  requires both an hdfs and impala 
        connnections in addition to ibis config and impala options for setting request_pool"""
 
        self.ibis_config=kwargs['ibis.config']
        self._set_ibis_config()
        self.hdfs_connect_kwargs=kwargs['hdfs.connect.kwargs']
        self.impala_connect_kwargs=kwargs['impala.connect.kwargs']
        self.impala_options=kwargs['impala.options']
        if command is not None:
            self.command=command
            
    def _set_ibis_config(self):
        for k in self.ibis_config.keys():
            ibis.config.set_option(k,self.ibis_config[k])
            
    def hdfs(self):
        return ibis.hdfs_connect(**self.hdfs_connect_kwargs)
    
    def impalaClient(self):
        kwargs=self.impala_connect_kwargs
        kwargs.update({'hdfs_client':self.hdfs()})
        client=ibis.impala.connect(**kwargs)
        client.set_options(self.impala_options)
        return client
    
    def qry(self,qry,r_type="df",limit=30):
        r_type = 'df' if r_type=='raw' else r_type
        qry=standard_conn_qry(qry)
        if r_type=="cmd":
            return(qry)
        client = self.impalaClient()
        for q in qry[:-1]:
            client.raw_sql(q,False)
        if r_type=="disp" and "LIMIT" not in qry[-1].split()[-2].upper() and "SELECT" in qry[-1].split()[1].upper():
            qry[-1] = qry[-1] + " LIMIT " + str(limit)
        if no_return(qry[-1]):
            return(None)
        if r_type in ("df","disp"):
            rslt = client.sql(qry[-1]).execute()
            if r_type=="disp":
                pretty(rslt,col="#E07862")
                rslt=None
        elif r_type=="msg":
            #TODO: Add messaging capability
            rslt=None
        else:
            rslt=None
        client.close()
        return(rslt)
