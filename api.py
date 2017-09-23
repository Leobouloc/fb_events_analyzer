#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:27:07 2017

@author: leo
"""
from flask import Flask, jsonify, request, send_file, url_for, render_template
from flask_session import Session
from werkzeug.utils import secure_filename

from main import find_subgroup

# Redis imports
#from rq import cancel_job as rq_cancel_job, Queue
#from rq.job import Job
#from worker import conn, VALID_QUEUES


#==============================================================================
# INITIATE APPLICATION
#==============================================================================

# Initiate application
app = Flask(__name__)

Session(app)

app.debug = True
app.config['SECRET_KEY'] = open('secret_key.txt').read()
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024 # Check that files are not too big (10GB)
app.config['ALLOWED_EXTENSIONS'] = ['csv', 'xls', 'xlsx', 'zip']
        

# Redis connection
#q = dict()
#for q_name in VALID_QUEUES:
#    q[q_name] = Queue(q_name, connection=conn, default_timeout=1800)
#            


#==============================================================================
# Error handling
#==============================================================================


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('URL not valid: %s', (error))
    return jsonify(error=True, message=error.description), 404

@app.errorhandler(405)
def method_not_allowed(error):
    app.logger.error('Method not allowed (POST or GET): %s', (error))
    return jsonify(error=True, message=error.description), 404



#==============================================================================
# GENERIC API METHODS (NORMALIZE AND LINK)
#==============================================================================

@app.route('/')
def home():
    return render_template('index.html')
    
def extract_id(url):
    return url.strip('/').split('events/')[1].split('/')[0]

@app.route('/api/find_subgroup/', methods=['POST'])
def api_find_subgroup():
    
    res = request.json
   
    query_a = [(extract_id(q['url']), q['statuses']) for q in res['a']]
    query_b = [(extract_id(q['url']), q['statuses']) for q in res['b']]
    
    print(query_a)
    print(query_b)
    
    print(query_a)
    print(query_b)
    relation = '1_in_2'
    
    result, data_a, data_b, names = find_subgroup(query_a, relation, query_b)
    
    to_return = {
                'a_and_b': len(result),
                'a': len(data_a),
                'b': len(data_b)
                }
    
    return jsonify(to_return)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
