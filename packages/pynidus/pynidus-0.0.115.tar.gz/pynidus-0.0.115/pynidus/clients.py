import json
import pandas as pd
import elasticsearch
import psycopg2
from google.cloud import storage

class ElasticsearchClient:
    
    def __init__(self, config):
        self.host = config.get('HOST')
        self.user = config.get('USER')
        self.password = config.get('PASSWORD')
        self._es = self._connect()
    
    def _connect(self):
        return elasticsearch.Elasticsearch(
            hosts=[self.host],
            http_auth=(self.user, self.password)
        )
    
    def query(self, index, body):
        return self._es.search(index=index, body=body)
         
class DatabaseClient:

    def __init__(self, config):
        self.host = config.get('HOST')
        self.database = config.get('DATABASE')
        self.user = config.get('USER')
        self.password = config.get('PASSWORD')
    
    def _connect(self):
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
    
    def query(self, query_):
        con = self._connect()
        table = pd.read_sql(sql=query_, con=con)
        con.close()
        return table
    
class GCSClient:
    
    def __init__(self, config):
        self.bucket = config.get('BUCKET')
        self.blob = config.get('BLOB')
        self._client = self._connect()
        
    def _connect(self):
        return storage.Client()
    
    def upload(self, obj):
        self._client.get_bucket(self.bucket).get_blob(self.blob).upload_from_string(
            data=json.dumps(obj),
            content_type='application/json'
        )