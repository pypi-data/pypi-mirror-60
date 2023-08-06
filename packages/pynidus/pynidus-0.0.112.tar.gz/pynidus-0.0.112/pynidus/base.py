from pynidus.clients import ElasticsearchClient, DatabaseClient, GCSClient

class MLTBase:
    
    def __init__(self, **kwargs):

        if kwargs.get('es_config'):
            self.es_client = ElasticsearchClient(kwargs.get('es_config'))
        
        if kwargs.get('pg_config'):
            self.pg_client = DatabaseClient(kwargs.get('pg_config'))
            
        if kwargs.get('gcs_config'):
            self.gcs_client = GCSClient(kwargs.get('gcs_config')) 