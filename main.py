#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 04:04:55 2017

@author: leo

Trying fb API

Find people in common in events statuses.

"""
import json
import os
import requests

import pandas as pd

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
    
    if (not os.path.isfile(file_path)) or force:
        resp = requests.get(url)
        print(resp.content)
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
    
def fetch(event_id, status):
    '''
    Return the data component of all users with a given status for a given event_id
    '''
    data = []
    for res in fetch_data(event_id, status):
        data.extend(res['data'])
    return data

if __name__ == '__main__':
    # Read secret app token (can be generated in Facebook API explorer)    
    token = open('my_secret_token.txt').read()
    
    # Event ID's
    aoutside_ids = {4: '521072081281160',
                   5: '755288111181519', 
                   6: '1612257909059435', 
                   8: '108507509757806'}
    
    # FB API statuses
    statuses = ['attending', 'maybe', 'interested', 'noreply']
    
    # Fetch ids for all evenets, and all statuses
    aoutside = dict()
    names = dict()
    for edition, event_id in aoutside_ids.items():
        aoutside[edition] = dict()
        for status in statuses:
            aoutside[edition][status] = {x['id'] for x in fetch(event_id, status)}
            names.update({x['id']: x['name'] for x in fetch(event_id, status)})
        
    # Create new fields with set of all users that are aware of the event (invited, participating, etc.)
    aoutside[8]['invited_or_participating'] = set()
    for status in statuses:
        aoutside[8]['invited_or_participating'] |= aoutside[8][status]
        
    # Find those that were participating at previous festivals and not invited or participating
    forgotten = set()
    for i, edition in enumerate([6, 5, 4]):
        n = len(aoutside[edition]['attending'] - aoutside[8]['invited_or_participating'] - forgotten)
        forgotten |= aoutside[edition]['attending'] - aoutside[8]['invited_or_participating']
        if i == 0:
            word = ''
        else:
            word = 'more '
        print('FB: {0} {1}participants from aoutside {2} were not invited to aoutside 8'.format(n, word, edition))
    
    # Write as csv file
    tab = pd.DataFrame([[id_, names[id_]] for id_ in forgotten])
    tab.columns = ['id_fb', 'name']
    tab.to_csv('aoutside_forgotten.csv', sep=';', encoding='utf-8', index=False)
