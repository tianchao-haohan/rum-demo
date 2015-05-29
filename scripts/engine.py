import threading
import zmq, json
import psycopg2, psycopg2.extras
import ConfigParser
from watcher import Watcher
from elasticsearch import Elasticsearch
from datetime import datetime
import pytz, time

config = ConfigParser.ConfigParser()
config.readfp(open("/etc/intflow/config.ini", "rb"))

db_host = config.get('postgresql', 'host')
db_port = int(config.get('postgresql', 'port'))
db_user = config.get('postgresql', 'user')
db_password = config.get('postgresql', 'password')
db_name = config.get('postgresql', 'db')

es_index = config.get('elasticsearch', 'index')
es_host = config.get('elasticsearch', 'host')
es_port = config.get('elasticsearch', 'port')

tz = config.get('intflow', 'timezone')

#print "%s %s %s %s %s\n" % (db_host, db_port, db_user, db_password, db_name)

context = zmq.Context(1)

def get_service_list ():
    service_list = []
    try:
        conn=psycopg2.connect(host = db_host, user = db_user, password = db_password, database = db_name, port = db_port)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('select * from cmdb_service')
        service_list = cur.fetchall()
        print "service_list: %s\n" % service_list
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print "Postgresql Error %s" % (e)

    return service_list


def notify ():
    print "notify...\n"
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:6558")

    request = context.socket (zmq.REQ)
    request.connect ("tcp://127.0.0.1:58000")

    while True:
        receiver.recv()

        service_list = get_service_list()

        updateProfileDict = {}
        updateProfileDict ['command'] = 'update_profile'
        updateProfileDict ['body'] = service_list
        request.send_json (updateProfileDict)
        print request.recv_json ()

def register ():
    print "server...\n"
    sock = context.socket(zmq.REP)
    sock.bind("tcp://*:58000")
    while True:
        message = sock.recv()
        print "message: %s\n" % message
        service_list = get_service_list()
        sock.send (json.dumps(service_list))

def adapter ():
    print "adapter...\n"
    es = Elasticsearch()
    context = zmq.Context ()

    bkdRecvSock = context.socket (zmq.PULL)
    bkdRecvSock.bind ("tcp://*:59009")
    while True:
        try:
            data = bkdRecvSock.recv ()                                                                                                                   
            breakdown = json.loads (data)
            timestamp = breakdown['@timestamp']
            proto = breakdown['protocol']
            dt = datetime.utcfromtimestamp(timestamp)
            dt_str = str(dt.date())
            dt2 = dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz))
            breakdown['@timestamp'] = dt2
            breakdown['type'] = proto.lower() + "_network"
            dt_str = dt_str.replace('-', '.')
            index_name = es_index + '-' + dt_str

            es.index(index=index_name, doc_type=breakdown['type'], body=breakdown)
        except Exception , e:
            time.sleep (2)
            es = Elasticsearch()
            continue

Watcher()
t1 = threading.Thread(target=notify)
t2 = threading.Thread(target=adapter)
t1.start()
t2.start()
