#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 04:04:55 2017

@author: leo

# Get token here https://developers.facebook.com/tools/explorer/
"""
import json
import os
import requests

try:
    import pandas as pd
except:
    print('WARNING: pandas is missing. to_csv is not usable')

# Read secret app token (can be generated in Facebook API explorer)    
token = open('my_secret_token.txt').read().strip()
TEMPLATE_URL = 'https://graph.facebook.com/{0}/{1}?limit=10000&access_token=' + token

def gen_file_name(url):
    '''Generate a name for the file returned by the url'''
    before_access_token = url.split('access_token=')[0]
    after_access_token = url.split('access_token=')[1].split('&', 1)
    if len(after_access_token) >= 2:
        after_access_token = '&' + after_access_token[1]
    else:
        after_access_token = ''
    return str(hash(before_access_token + after_access_token)).replace('-', 'm')
    
def fetch_url(dir_name, url, force=False):
    '''Retrieve the content of the given url. Use cache unless force==True'''
    file_name = gen_file_name(url)
    file_path = os.path.join(dir_name, file_name)
    
    #print(url)
    print(file_path)
    
    if (not os.path.isfile(file_path)) or force:
        resp = requests.get(url)
        with open(file_path, 'wb') as w:
            w.write(resp.content)

    with open(file_path) as f:
        return json.load(f)

    
def fetch_data(event_id, status, force=False):
    '''
    Generate results for fetching  users for a given event_id with a given status 
    ('attending', 'maybe', 'interested', 'noreply'). Use cache unless force==True
    '''
    dir_name = os.path.join('data', event_id)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    
    url = TEMPLATE_URL.format(event_id, status)
    while url is not None:
        res = fetch_url(dir_name, url, force)
        url = res.get('paging', {}).get('next')
        yield res
    
def fetch(event_id, status, force=False):
    '''
    Return the data component of all users with a given status for a given event_id
    '''
    data = []
    for res in fetch_data(event_id, status, force):
        if 'error' in res:
            raise Exception('Error fetching data:\n{0}'.format(json.dumps(res)))
        data.extend(res['data'])
    return data

def _r_i_l(statuses):
    '''r_i_l: reformat_input_lower'''
    if isinstance(statuses, str):
        return [statuses]
    elif isinstance(statuses, list):
        return statuses
    else:
        raise TypeError('"statuses" should be of type str or list; got {0} instead'.format(type(statuses)))

def _r_i_h(events):
    '''r_i_h: reformat_input_higher'''
    if isinstance(events, tuple):
        return [events]
    elif isinstance(events, list):
        return events
    else:
        return TypeError('"events" should be of type tuple or list (of tuples)')

def fetch_multiple(events, force=False):
    '''
    INPUT:
        - events: tuple or list of tuple (event_id, status) or (event_id, [status, ...])
                    or [(event_id, status), ...] or [(event_id, [status, ...]), ]
    '''
    names = dict()
    data = dict()
    for (id_, statuses) in events:
        data[id_] = dict()
        for status in statuses:
            fetch_res = fetch(id_, status, force)
            data[id_][status] = {x['id'] for x in fetch_res}            
            names.update({x['id']: x['name'] for x in fetch_res})
    return data, names

def aggregate_multiple(data):
    '''Create a set aggregating the result of fetch_multiple'''
    data_agg = set()
    for val_id in data.values():
        for val_status in val_id.values():   
            data_agg |= val_status
    return data_agg

def find_subgroup(events_1, relation, events_2, force=False):
    '''
    INPUT:
        - events_1: tuple or list of tuple (event_id, status) or (event_id, [status, ...])
                    or [(event_id, status), ...] or [(event_id, [status, ...]), ]
        - relation: '1_in_2' or '1_not_in_2'. 
                    '1_in_2' will look for the common subgroup of people to events_1 and events_2
                    '1_not_in_2' will look for the group of people that are included
                             in events_1 but not events_2
        - events_2: same format as events_1
        - force: force re-download
    
    OUTPUT:
        - result: resulting set of users
        - data_1_glob: object with data of events_1
        - data_2_glob: object with data of events_2

    '''
    # Input as [(event_id, [status, ...]), ]
    events_1 = [(id_, _r_i_l(statuses)) for (id_, statuses) in _r_i_h(events_1)]
    events_2 = [(id_, _r_i_l(statuses)) for (id_, statuses) in _r_i_h(events_2)]

    # Fetch multiple events
    data_1, names = fetch_multiple(events_1, force=False)
    data_2, names_2 = fetch_multiple(events_2, force=False)
    names.update(names_2)
    
    # Aggregate
    data_1_glob = aggregate_multiple(data_1)
    data_2_glob = aggregate_multiple(data_2)

    # Compute output
    if relation == '1_in_2':
        result = data_1_glob & data_2_glob
    elif relation == '1_not_in_2':
        result = data_1_glob - data_2_glob
        
    # Join with names
    return result, data_1_glob, data_2_glob, names
    
def to_csv(ids, names, *argv, **kwargs):
    '''
    Create a CSV file from a list of ids and a dict of id->name.
    This is a wrapper around pandas.to_csv ; all options can be used
    '''
    tab = pd.DataFrame([[id_, names[id_]] for id_ in ids])
    tab.columns = ['id_fb', 'name']
    return tab.to_csv(*argv, index=False, **kwargs)    

def size(data_glob):
    return len(data_glob)

if __name__ == '__main__':
    
    # Get all people that were marked as attending for event 1
    request_1 =  ('1612257909059435', 'attending')
    
    # Get all people invited to event 2
    request_2 =  ('108507509757806', ['attending', 'maybe', 'interested', 'noreply'])
    
    # Look for the subgroup of people that are in group 1 but not in group 2
    # In our case: the people that attended event 1 but weren't invited to event 2
    relation = '1_in_2'
    
    # Compute
    result, data_1, data_2, names = find_subgroup(request_1, relation, request_2)
    
    # Count the size of the output group
    print('Number of people in the resulting group:', len(result))
    
    # Write the list of ids and names to csv file
    file_path = 'people_to_invite.csv'
    to_csv(result, names, file_path)
    


#    # Event ID's
#    aoutside_ids = {4: '521072081281160',
#                   5: '755288111181519', 
#                   6: '1612257909059435', 
#                   8: '108507509757806'}     