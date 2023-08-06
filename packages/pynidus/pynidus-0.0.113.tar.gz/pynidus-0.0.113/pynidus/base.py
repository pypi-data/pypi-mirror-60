import os
from pynidus.clients import ElasticsearchClient, DatabaseClient, GCSClient

class MLTBase:
    
    def __init__(self, **kwargs):

        envs = kwargs.get('envs')

        if kwargs.get('es_config'):
            es_config = kwargs.get('es_config')
        elif envs.get('ELASTICSEARCH'):
            es_config = {
                'HOST': os.getenv('ES_HOST'),
                'USER': os.getenv('ES_USER'),
                'PASSWORD': os.getenv('ES_PASSWORD')
            }
        else:
            es_config = None
            
        if es_config:
            self.es_client = ElasticsearchClient(es_config)

        if kwargs.get('pg_config'):
            pg_config = kwargs.get('pg_config')
        elif envs.get('POSTGRESQL'):
            pg_config = {
                'HOST': os.getenv('PG_HOST'),
                'USER': os.getenv('PG_USER'),
                'PASSWORD': os.getenv('PG_PASSWORD'),
                'DATABASE': os.getenv('PG_DATABASE')
            }
        else:
            pg_config = None

        if pg_config:
            self.pg_client = DatabaseClient(pg_config)
         
        if kwargs.get('gcs_config'):
            gcs_config = kwargs.get('gcs_config')        
        elif envs.get('GCS'):
            gcs_config = {
                'BUCKET': os.getenv('BUCKET'),
                'BLOB': os.getenv('BLOB')
            }
        else:
            gcs_config = None
            
        if gcs_config:
            self.gcs_client = GCSClient(gcs_config)

        


