# Facebook Event Attendees Compare
This tool is made to answer questions such as: **"How many users attended my previous events and were not even invited to the next one ?"**. It allows you to group users by status at event attendance and compare various public events.

It takes care of fetching the data and caching it properly. All you have to do is:
- get a facebook API token (1 minute)
- configurate the tool with the ids and statuses you want to compare

# Install

No install yet, just clone the script and configurate in `main.py`.

## Requirements

Optional `pandas`

# How to use

## Get a facebook api token
This tool relies on the facebook API which means you will need an API token. For a one-shot use, you can easily get a token one by creating a dummy application and using the API explorer: https://developers.facebook.com/tools/explorer/ (no specific permissions needed).

Once you get this token, you should write it to a file `my_secret_token.txt` in the same directory as the `main.py` file

## Use Example

```
    # Get all people that were marked as attending for event with id 1612257909059435
    query_1 =  ('1612257909059435', 'attending')
    
    # Get all people invited (all statuses) to event with id 108507509757806
    query_2 =  ('108507509757806', ['attending', 'maybe', 'interested', 'noreply'])
    
    # Look for the subgroup of people that are in group 1 but not in group 2
    # In our case: the people that attended event 1 but weren't invited to event 2
    relation = '1_in_2'
    
    # Compute
    result, data_1, data_2, names = find_subgroup(query_1, relation, query_2)
    
    # Count the size of the output group
    print('Number of people in the resulting group:', len(result))
    
    # Write the list of ids and names to csv file
    file_path = 'people_to_invite.csv'
    to_csv(result, names, file_path)
```
## Main objects

- `event_id`: the facebook ID that appears in the URL of a public event (the event_id for www.facebook.com/events/108507509757806/ is 108507509757806)
- `status`: the status of the person mentioned in an event. Can be any of:
  - 'attending'
  - 'maybe' 
  - 'interested'
  - 'noreply' : person was invited but did not answer
- `query`: a custom syntax to ask to fetch a group of people by event_id and status. This can be any of the following formats:
  - `('event_id_XYZ', 'attending')` : 1 ID, 1 status
  - `('event_id_XYZ', ['attending', 'interested'])` : 1 ID, multiple statuses
  - `[('event_id_XYZ', 'attending'), ('event_id_ABC', 'interested', 'maybe')]` : a union of multiple single event queries
- `relation`: the relation between 2 groups of users (group_1 and group_2). Can be:
  - '1_in_2' : find elements of group_1 that are also in group_2
  - '1_not_in_2' : find elements of group_1 that are not in group_2 

## Main functions

- `fetch_multiple(query, force=False)` : fetch the data associated to a query (see above).
- `find_subgroup(query_1, relation, query_2)` : perform queries for query_1 and query_2 and compute the subgroup according to the requested relation
- `to_csv(result, names, file_path)` : write the list of people resulting of `fetch_multiple` or `find_subgroup`

# Contribute
Please feel free to leave issues or make pull requests :)
