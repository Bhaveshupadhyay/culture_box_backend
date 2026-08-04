import typesense
from app.core.config import settings

_client = None

def get_typesense_client() -> typesense.Client:
    global _client
    if _client is None:
        _client = typesense.Client({
            'nodes': [{
                'host': settings.TYPESENSE_HOST,
                'port': settings.TYPESENSE_PORT,
                'protocol': settings.TYPESENSE_PROTOCOL,
            }],
            'api_key': settings.TYPESENSE_API_KEY,
            'connection_timeout_seconds': 2
        })
    return _client
