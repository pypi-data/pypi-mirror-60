import os
from pynidus.clients import ElasticsearchClient, DatabaseClient, GCSClient

class MLTBase:
    
    def __init__(self, **kwargs):
        
        env = os.getenv('ENV')

        if env:

            es_config = {
                'HOST': os.getenv('ES_HOST'),
                'USER': os.getenv('ES_USER'),
                'PASSWORD': os.getenv('ES_PASSWORD')
            }

            pg_config = {
                'HOST': os.getenv('PG_HOST'),
                'USER': os.getenv('PG_USER'),
                'PASSWORD': os.getenv('PG_PASSWORD'),
                'DATABASE': os.getenv('PG_DATABASE')
            }

            gcs_config = {
                'BUCKET': os.getenv('BUCKET'),
                'BLOB': os.getenv('BLOB')
            }

        else:

            es_config = kwargs.get('es_config')
            pg_config = kwargs.get('pg_config')
            gcs_config = kwargs.get('gcs_config')

        if es_config:
            self.es_client = ElasticsearchClient(es_config)

        if pg_config:
            self.pg_client = DatabaseClient(pg_config)

        if gcs_config:
            self.gcs_client = GCSClient(gcs_config)

        


