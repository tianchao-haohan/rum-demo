import threading
import zmq, json
import psycopg2, psycopg2.extras
import ConfigParser
from watcher import Watcher
from elasticsearch import Elasticsearch
from datetime import datetime
from threading import Lock
import pytz

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

agent_list = {}
agent_list_lock = Lock()

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

def service_thread():
    recv = context.socket(zmq.REP)
    recv.bind("tcp://*:60001")
    while True:
        try:
            data = recv.recv();
            agent_info = json.loads(data)
            if(agent_info["command"] == "register"):
                agent_body = agent_info["body"]
                agent_ip = agent_body["ip"]
                agent_port = agent_body["port"]
                try:
                    agent_list_lock.acquire()
                    agent_list[agent_ip] = agent_port
                finally:
                    agent_list_lock.release()
                register_result = {};
                register_result["code"] = 0
                register_result["body"] = ""
                recv.send_json(register_result)
        except Exception as e:
            print "service update exception: %s" % e
            continue

                

def notifyAllAgent():
    req = context.socket(zmq.REQ)
    service_list = get_service_list()
    profile_body = {}
    message = {}
    try:
        agent_list_lock.acquire()
        for ip in agent_list:
            socket_info = "tcp://" + ip + ":" + str(agent_list[ip])
            req.connect(socket_info)

            profile_body['application_services'] = service_list
            message['command'] = 'update_profile'
            message['body'] = profile_body
            req.send_json(message)


    finally:
        agent_list_lock.release()

def notify ():
    print "notify...\n"
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:60008")

    while True:
        try:
            receiver.recv()

            notifyAllAgent()
        except Exception as e:
            print "GUI notification exception: %s" % e
            continue


def adapter ():
    print "adapter...\n"
    es = Elasticsearch()
    context = zmq.Context ()

    bkdRecvSock = context.socket (zmq.PULL)
    bkdRecvSock.bind ("tcp://*:60002")
    while True:
        try:
            data = bkdRecvSock.recv ()                                                                                                                   
            breakdown = json.loads (data)
        
            timestamp = breakdown['timestamp']
            proto = breakdown['protocol']
        
            dt = datetime.utcfromtimestamp(timestamp)
            dt_str = str(dt.date())
            dt2 = dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz))
            breakdown['@timestamp'] = dt2
            breakdown['type'] = proto.lower() + "_network"
            dt_str = dt_str.replace('-', '.')
            index_name = es_index + '-' + dt_str
            print "breakdown: %s\n" % breakdown
            es.index(index=index_name, doc_type=breakdown['type'], body=breakdown)

        except Exception as e:
            print "ES adapter exception: %s" % e
            continue


Watcher()
threads = []
t1 = threading.Thread(target=notify)
threads.append (t1)
t1.start()

t2 = threading.Thread(target=adapter)
threads.append (t2)
t2.start()

t3 = threading.Thread(target = service_thread)
threads.append (t3)
t3.start()

for t in threads:
    t.join()

print "Exiting Main Thread"
