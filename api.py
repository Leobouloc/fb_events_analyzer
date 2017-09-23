#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:27:07 2017

@author: leo
"""
from flask import Flask, jsonify, request, send_file, url_for, render_template
from flask_session import Session
from werkzeug.utils import secure_filename

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

@app.route('/api/find_subgroup/', methods=['POST'])
def find_subgroup(project_type):
    flask.req
    result, data_1, data_2, names = find_subgroup(query_1, relation, query_2)
    return jsonify(error=False, 
                   project_id=proj.project_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
