#!/usr/bin/env python2

from sqlite3 import connect
from datetime import datetime, timedelta
from functools import update_wrapper
from glob import glob
from json import load, loads
from uuid import uuid4

from flask import Flask, jsonify, make_response, request, g, abort, session, current_app
from jsonschema import validate, FormatChecker
from pytz import utc
from requests import post
from strict_rfc3339 import validate_rfc3339

import traceback



app = Flask(__name__)
app.config.from_envvar('FLASK_SETTINGS_FILE')



DEBUG = True
SQL_SCHEMA_FILES = './sql/*.sql'
JSON_SCHEMA_FILE = 'jsonschema.json'
EARLIEST_DATETIME = datetime(2013, 11, 7, 0, 0, 0, 0, utc)
ACCEPTABLE_FUTURE_TIMEDELTA = timedelta(days=1)



# General db stuff.
###################

def connect_db():
    return connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# For CLI usage.
# FIXME: Unused at the moment.
def init_db():
    with app.app_context():
        db = get_db()
        is_db_inited = query_db(
                """SELECT CASE
                       WHEN EXISTS (SELECT * FROM SchemaVersion LIMIT 1) THEN 1
                       ELSE 0
                   END""")
        if not is_db_inited:
            for fname in sorted(glob.glob(SQL_SCHEMA_FILES)):
                print 'sql schema file'
                print name
                with app.open_resource(fname, mode='r') as f:
                    db.cursor().executescript(f.read())
            db.commit()

def query_db(query, args=(), do_commit=False, one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def write_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()



# General app stuff.
####################

# FIXME: Remove later, use reverse proxy.
# From address: http://flask.pocoo.org/snippets/56/
# Public domain.
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/")
def hello():
    return "Hello World!"



# Time functionality.
#####################

def microsecond_int_to_millisecond_str(mu):
    # mu should not be negative but let's not keel over if it happens.
    mu = max(0, mu)
    return (str(int(round(mu, -3)))[:-3]).zfill(3)

def datetime_to_sql_timestamp(dt):
    millisecond_str = microsecond_int_to_millisecond_str(dt.microsecond)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.') + millisecond_str

def timestamp_str():
    dt = utc.localize(datetime.utcnow())
    return datetime_to_sql_timestamp(dt)

def js_timestamp_to_datetime(string):
    return utc.localize(datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ'))

def validate_timestamp(ts_str):
    dt = js_timestamp_to_datetime(ts_str)
    if (dt < EARLIEST_DATETIME or
            dt >= utc.localize(datetime.utcnow()) +
                  ACCEPTABLE_FUTURE_TIMEDELTA):
        raise ValueError("Timestamp too old or too much in the future.")



# JSON Schema functionality.
############################

def open_json_schema():
    with open(JSON_SCHEMA_FILE, 'r') as f:
        return load(f)

def validate_json_schema(d):
    validate(d, json_schema)



# Session functionality.
########################

def open_session(session_id, user_agent, logged_in_utc):
    write_db("""INSERT INTO Sessions (session_id, user_agent, logged_in_utc)
                VALUES (?, ?, ?)""",
             (str(session_id), user_agent, logged_in_utc))

def is_session_id_in_db(session_id):
    res = query_db("""SELECT session_id FROM Sessions
                      WHERE session_id == ?""",
                   (str(session_id), ))
    # FIXME: Smarter way?
    return True if res else False

def create_session_id(user_agent):
    is_id_unique = False
    while not is_id_unique:
        session_id = uuid4()
        if not is_session_id_in_db(session_id):
            is_id_unique = True
    ts = str(datetime.utcnow()) + ' UTC'
    open_session(session_id, user_agent, ts)
    return session_id

def validate_session_id(session_id):
    if not is_session_id_in_db(session_id):
        raise ValueError('session_id was not found.')
    return session_id

# FIXME: Remove crossdomain later, use reverse proxy
@app.route('/auth/login', methods=['GET'])
@crossdomain(origin='*')
def login():
    user_agent = request.headers.get('User-Agent')
    session_id = create_session_id(user_agent or "")
    if session_id:
        return make_response(jsonify(sessionId = session_id), 200)
    abort(500)

## FIXME: Remove crossdomain later, use reverse proxy
# FIXME: Not needed currently.
@app.route('/auth/logout', methods=['POST'])
@crossdomain(origin='*')
def logout():
    return make_response(jsonify({'sessionId': ''}), 200)



# Trace functionality.
######################

def is_trace_id_in_db(trace_id):
    res = query_db("""SELECT trace_id FROM Traces
                      WHERE trace_id == ?""",
                      (str(trace_id), ))
    # FIXME: Smarter way?
    return True if res else False

def write_trace_in_db(session_id, trace):
    is_trace_id_unique = False
    while not is_trace_id_unique:
        trace_id = uuid4()
        if not is_trace_id_in_db(trace_id):
            is_trace_id_unique = True

    loc = trace['location']
    latlng = loc['latlng']
    bounds = loc['bounds']
    ne = bounds['northEast']
    sw = bounds['southWest']

    write_db("""INSERT INTO Traces (trace_id, session_id, timestamp_utc,
                                    accuracy, lat, lng, ne_lat, ne_lng,
                                    sw_lat, sw_lng)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
             (str(trace_id), str(session_id), trace['timestamp'],
              loc['accuracy'], latlng['lat'], latlng['lng'], ne['lat'],
              ne['lng'], sw['lat'], sw['lng']))

# FIXME: Remove crossdomain later, use reverse proxy
@app.route("/trace_seqs", methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='content-type')
def save_trace_seq():
    try:
        req = request.get_json()
        validate_json_schema(req)
        session_id = validate_session_id(req['session_id'])
        trace_seq = req['trace_seq']

        for trace in trace_seq:
            validate_timestamp(trace['timestamp'])
    # FIXME: Be more specific with errors.
    except Exception as e:
        print(e)
        abort(400)

    try:
        for trace in trace_seq:
            # FIXME: If not unique timestamp, it's a user error 400.
            write_trace_in_db(session_id, trace)
        # FIXME: Or 200, as the resource is not shown to user?
        return make_response(jsonify({"status": "OK"}), 201)
    except Exception as e:
        print(e)
        abort(500)



# Adds date-time checking.
# FIXME: Is this really how it's supposed to be done?
FormatChecker.cls_checks("date-time", ())(validate_rfc3339)

json_schema = open_json_schema()



if __name__ == "__main__":
    app.run()
