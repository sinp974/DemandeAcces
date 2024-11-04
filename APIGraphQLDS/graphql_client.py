# Connexion et configuration de GraphQL


from gql import Client
from gql.transport.requests import RequestsHTTPTransport



def create_graphql_client(api_url, api_key, proxies):
    """_summary_

    Args:
        api_url (str): Url utilisee pour acceder a l'API
        api_key (str): Jeton d'acces a l'API
        proxies (dict): Parametrage des proxies

    Returns:
        gql.client.Client: client GraphQL permettant l'echange avec l'API de Demarches Simplifiees
    """
    transport = RequestsHTTPTransport(
        url=api_url,
        headers={'Authorization': f'Bearer {api_key}'},
        use_json=True,
        timeout=100,
        proxies=proxies
    )
    return Client(transport=transport, fetch_schema_from_transport=True)
