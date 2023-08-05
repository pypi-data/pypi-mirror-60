import requests

from imis.utils import generic_property_data_collection_to_dict


def _raw_iqa_results(client, query_name, offset=0, *parameters):
    headers = {'Authorization': client.auth.authorization_header}
    url = client.url + f'/api/iqa?QueryName={query_name}&offset={offset}'
    for param in parameters:
        url += f'&parameter={param}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    yield data
    if data['HasNext']:
        yield from _raw_iqa_results(client, query_name, data['NextOffset'], *parameters)


def iter_items(client, query_name, offset=0, *parameters):
    for page in _raw_iqa_results(client, query_name, *parameters):
        for item in page['Items']['$values']:
            yield generic_property_data_collection_to_dict(item['Properties'])
