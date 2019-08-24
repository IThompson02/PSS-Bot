

import pss_core as core


def get_alliance_users(alliance_id):
    url = f'{core.get_base_url()}AllianceService/ListUsers?allianceId={alliance_id}&skip=0&take=100'



def search_alliances(alliance_name):
    url = f'{core.get_base_url()}AllianceService/SearchAlliances?name={alliance_name}&skip=0&take=100'
    raw_data = core.get_data_from_url(url)
    data = core.xmltree_to_dict3(raw_data)
    result = [data[key] for key in data.keys()]
    return result