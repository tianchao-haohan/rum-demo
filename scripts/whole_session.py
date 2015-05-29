import os, time, random
import json, zmq
import threading
from threading import Thread, local  
import copy

from watcher import Watcher


srv_ip = '127.0.0.1'
srv_port = 59009


#P_DEFAULT = "DEFAULT"
P_HTTP = "HTTP"
P_MYSQL = "MYSQL"

context = zmq.Context()
#gi = pygeoip.GeoIP('/usr/share/GeoLiteCity.dat', pygeoip.MEMORY_CACHE)

period = 1

sbrk = {}
sbrk['protocol'] = P_HTTP

s0 = {'service_ip':'192.168.1.12', 'service_port':1235, 'protocol':P_HTTP}

s1 = {'service_ip':'10.20.30.40', 'service_port':5679, 'protocol':P_HTTP}

s2 = {'service_ip':'20.30.41.56', 'service_port':3306, 'protocol':P_MYSQL}

http_status_list = [200, 201, 202, 203, 300, 301, 302, 303, 400, 401, 402, 403, 404, 405, 406, 407, 410, 412, 414, 500, 501, 502, 503]
http_method_list = ['GET', 'POST', 'PUT', 'CONNECT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE']
http_reset_list = ["HTTP_RESET_TYPE1", "HTTP_RESET_TYPE2", "HTTP_RESET_TYPE3", "HTTP_RESET_TYPE4"]
mysql_statements = ["SELECT * from db where a =b;", "DELETE from db where a=b;", "UPDATE db SET date='2015-03-09 11:38:05' WHERE username='test'", "INSERT INTO db (username, body, date) VALUES ('user', 'test', '2015-03-09 11:38:05')"]
mysql_status_list = ['MYSQL_OK', 'MYSQL_OK', 'MYSQL_ERROR'] 
mysql_reset_list = ['MYSQL_RESET_TYPE1', 'MYSQL_RESET_TYPE2', 'MYSQL_RESET_TYPE3', 'MYSQL_RESET_TYPE4']


mutex_brkid = threading.Lock()
mutex_time = threading.Lock()

now_secs = int(time.time())
sbrk['@timestamp'] = now_secs #12345600
#print "now_secs: %d\n" % now_secs
sbrk['connection_id'] = 1
#sbrk['breakdown_id'] = 111
sbrk['source_ip'] = '192.168.1.11'
sbrk['source_port'] = 24567
sbrk['tcp_retries'] = 234
sbrk['tcp_retries_latency'] = 23
sbrk['tcp_duplicate_synacks'] = 456
sbrk['tcp_rtt'] = 200 
sbrk['tcp_mss'] = 789
sbrk['tcp_state'] = "TCP_CONNECTED"
sbrk['tcp_connection_latency'] = 234
sbrk['tcp_total_packets'] = 902
sbrk['tcp_total_bytes'] = 902
sbrk['tcp_tiny_packets'] = 903
sbrk['tcp_paws_packets'] = 904
sbrk['tcp_retransmitted_packets'] = 905
sbrk['tcp_out_of_order_packets'] = 906
sbrk['tcp_zero_windows'] = 907
sbrk['tcp_duplicate_acks'] = 908

def create_object (service):
    sbrk1 = copy.copy(sbrk)

    sbrk1['service_ip'] = service['service_ip']
    sbrk1['service_port'] = service['service_port']
    sbrk1['protocol'] = service['protocol'] 
    sbrk1['region_code'] = random.randint(1, 30)
    return sbrk1

def reset (sbrk1) :
    sbrk1['tcp_total_packets'] = 0
    sbrk1['tcp_tiny_packets'] = 0
    sbrk1['tcp_paws_packets'] = 0
    sbrk1['tcp_retransmitted_packets'] = 0
    sbrk1['tcp_out_of_order_packets'] = 0
    sbrk1['tcp_zero_windows'] = 0
    sbrk1['tcp_duplicate_acks'] = 0

    if sbrk1['protocol'] == "DEFAULT":
        sbrk1['default_exchange_size'] = 0
        sbrk1['default_server_latency'] = 0 

    elif sbrk1['protocol'] == "HTTP":   
        sbrk1['request_raw'] = ""
        sbrk1['http_request_line'] = ""
        sbrk1['http_request_version'] = ""
        sbrk1['http_method'] = "" 
        sbrk1['http_host'] = ""
        sbrk1['http_uri'] = ""
        sbrk1['http_user_agent'] = ''
        sbrk1['http_refer'] = ''
        sbrk1['http_accept'] = ''
        sbrk1['http_accept_language'] = ''
        sbrk1['http_accept_encoding'] = ''
        sbrk1['http_x_forwarded_for'] = ''
        sbrk1['http_request_connection'] = ''
        sbrk1['http_response_version'] = ''
        sbrk1['response_raw'] = ""
        sbrk1['http_state'] = ""
        sbrk1['http_status_code'] = 0
        sbrk1['http_response_phrase'] = ''
        sbrk1['http_content_type'] = ''
        sbrk1['http_content_length'] = ''
        sbrk1['http_content_disposition'] = ''
        sbrk1['http_transfer_encoding'] = ''
        sbrk1['http_response_connection'] = ''

        sbrk1['http_request_header_size'] = 0
        sbrk1['http_request_body_size'] = 0 
        sbrk1['http_response_header_size'] = 0 
        sbrk1['http_response_body_size'] = 0 
        sbrk1['http_server_latency'] = 0 
        sbrk1['http_download_latency'] = 0

    elif sbrk1['protocol'] == "MYSQL":   
        sbrk1['request_raw'] = '' 
        sbrk1['mysql_state'] = '' 
        sbrk1['mysql_server_version'] = ''
        sbrk1['mysql_user_name'] = ''         
        sbrk1['mysql_connection_id'] =  0 
        sbrk1['mysql_method'] =  ''
        sbrk1['mysql_query'] =  ''
        sbrk1['mysql_tables'] =  ''
        sbrk1['response_raw'] = '' 
        sbrk1['mysql_error_code'] = 0        
        sbrk1['mysql_sql_state'] = 0
        sbrk1['mysql_error_message'] = ''  

        sbrk1['mysql_request_size']  = 0    
        sbrk1['mysql_response_size'] = 0   
        sbrk1['mysql_server_latency'] = 0 

    return sbrk1

def simulate_aborted(service) :
    sock = context.socket(zmq.PUSH)
    sock.connect("tcp://%s:%s" % (srv_ip, srv_port))
    while True:
        time.sleep(18)
        sbrk1 = create_object (service)
        sbrk1['tcp_state'] = "TCP_RESET_TYPE1"

        if mutex_brkid.acquire(1):
            sbrk['connection_id'] = sbrk['connection_id'] + 1
            sbrk1['connection_id'] = sbrk['connection_id']
            mutex_brkid.release()

        reset (sbrk1)
        sbrk1['tcp_total_packets'] = 123

        now_secs = int(time.time())
        sbrk1['@timestamp'] = now_secs
        sock.send(json.dumps(sbrk1))

        sbrk2 = copy.copy(sbrk1)
        sbrk2['tcp_state'] = "TCP_RESET_TYPE2"
        if mutex_brkid.acquire(1):
            sbrk['connection_id'] = sbrk['connection_id'] + 1
            sbrk2['connection_id'] = sbrk['connection_id']
            mutex_brkid.release()

        now_secs = int(time.time())
        sbrk2['@timestamp'] = now_secs
        sock.send(json.dumps(sbrk2))

def simulate_connected(service, sock) :
    sbrk1 = create_object (service)
    sbrk1['tcp_state'] = "TCP_CONNECTED"
    connection_id = 0

    if mutex_brkid.acquire(1):
        sbrk['connection_id'] = sbrk['connection_id'] + 1
        sbrk1['connection_id'] = sbrk['connection_id']
        connection_id = sbrk1['connection_id']
        mutex_brkid.release()

    reset (sbrk1)
    sbrk1['tcp_total_packets'] = 213

    now_secs = int(time.time())
    sbrk1['@timestamp'] = now_secs
    sock.send(json.dumps(sbrk1))

    return connection_id

def get_mysql_error_code ():
    code = 0
    while True:
        code = random.randint(1000, 2061)
        if code > 1885 and code < 2000 :
            continue
        else:
            break

    return code

def fullfil_sbreakdown (sbrk1, connection_id, status_code, method) :
    sbrk1['connection_id'] = connection_id

    sbrk1['tcp_state'] = "TCP_DATA_EXCHANGING"
    sbrk1['tcp_retries'] = 0
    sbrk1['tcp_retries_latency'] = 0
    sbrk1['tcp_duplicate_synacks'] = 0
    sbrk1['tcp_rtt'] = 0 
    sbrk1['tcp_mss'] = 0
    sbrk1['tcp_connection_latency'] = 0
    sbrk1['tcp_total_packets'] = random.randint(800, 1000)
    sbrk1['tcp_total_bytes'] = random.randint(500, 1400)
    sbrk1['tcp_c2s_bytes'] = random.randint(100, 800)
    sbrk1['tcp_s2c_bytes'] = sbrk1['tcp_total_bytes'] - sbrk1['tcp_c2s_bytes']
    sbrk1['tcp_tiny_packets'] = random.randint(100, 300)
    sbrk1['tcp_paws_packets'] = random.randint(100, 300)
    sbrk1['tcp_retransmitted_packets'] = random.randint(0, 300)
    sbrk1['tcp_out_of_order_packets'] = random.randint(0, 300)
    sbrk1['tcp_zero_windows'] = random.randint(0, 300)
    sbrk1['tcp_duplicate_acks'] = random.randint(0, 300)

    if sbrk1['protocol'] == "DEFAULT":
        sbrk1['default_exchange_size'] = 0
        sbrk1['default_server_latency'] = 0

    elif sbrk1['protocol'] == "HTTP":   
        sbrk1['http_request_line'] = method + " /api/metrics/list HTTP/1.1"
        sbrk1['http_request_version'] = "HTTP 1.1"
        sbrk1['http_method'] = method
        sbrk1['http_host'] = 'test.com'
        sbrk1['http_uri'] = '/api/metrics/list HTTP/1.1'
        sbrk1['http_user_agent'] = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17    \
    (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17"
        sbrk1['http_refer'] = 'http://test.com/metrics'
        sbrk1['http_accept'] = 'application/json, text/javascript, */*; q=0.01'
        sbrk1['http_accept_language'] = 'en-US,en;q=0.8'
        sbrk1['http_accept_encoding'] = 'gzip,deflate,sdch'
        sbrk1['http_x_forwarded_for'] = '192.168.1.1,192.168.1.13'
        sbrk1['http_request_connection'] = 'Keep-alive'

        sbrk1['http_response_version'] = 'HTTP 1.0'
        sbrk1['http_content_type'] = 'application/json'
        sbrk1['http_content_disposition'] = ':'
        sbrk1['http_transfer_encoding'] = 'gzip'
        sbrk1['http_response_connection'] = 'Keep-alive'

        if status_code / 100 == 2 or status_code / 100 == 3 :
            sbrk1['http_state'] = "HTTP_OK"
            sbrk1['http_status_code'] = status_code
            sbrk1['http_response_phrase'] = 'OK'
        else :
            sbrk1['http_state'] = "HTTP_ERROR"

        sbrk1['http_status_code'] = status_code
        sbrk1['http_request_header_size'] = 345
        sbrk1['http_request_body_size'] = 356
        sbrk1['http_response_header_size'] = 456
        sbrk1['http_response_body_size'] = 457
        sbrk1['http_server_latency'] = random.randint(500, 1200)
        sbrk1['http_download_latency'] = random.randint(0, 300)
        sbrk1['http_response_latency'] = sbrk1['http_server_latency'] + sbrk1['http_download_latency']

    elif sbrk1['protocol'] == "MYSQL":   
        sbrk1['mysql_state'] = status_code
        sbrk1['mysql_server_version'] = "mysql 5.1"
        sbrk1['mysql_user_name'] = 'user'         
        sbrk1['mysql_connection_id'] = connection_id

        sbrk1['mysql_method'] =  'SELECT'
        sbrk1['mysql_request_statement'] =  "SELECT post.id AS post_id, post.username AS post_username, \
post.title AS post_title, post.body AS post_body, post.pub_date AS post_pub_date \
FROM post ORDER BY post.pub_date"

        if status_code == "MYSQL_OK" :
            sbrk1['mysql_error_code'] = 0        
            sbrk1['mysql_sql_state'] = 0
            sbrk1['mysql_error_message'] = ''  
            sbrk1['mysql_request_size']  = 1024
            sbrk1['mysql_response_size'] = 9000
            sbrk1['mysql_server_latency'] = random.randint(500, 1200)
            sbrk1['mysql_download_latency'] = random.randint(0, 300)
        else :
            sbrk1['mysql_error_code'] = get_mysql_error_code()         
            sbrk1['mysql_sql_state'] = 1
            sbrk1['mysql_error_message'] = 'test'  
            sbrk1['mysql_request_size']  = 512
            sbrk1['mysql_response_size'] = 499

            sbrk1['mysql_server_latency'] = random.randint(100, 300)
            sbrk1['mysql_download_latency'] = 0

        sbrk1['mysql_response_latency'] = sbrk1['mysql_server_latency'] + sbrk1['mysql_download_latency']
    return sbrk1

def simulate_exchanging(service, connection_id, status_code, method, sock) :
    sbrk1 = create_object (service)
    sbrk1 = fullfil_sbreakdown (sbrk1, connection_id, status_code, method)

    time.sleep(12)
    now_secs = int(time.time())
    sbrk1['@timestamp'] = now_secs
    sock.send(json.dumps(sbrk1))

###END

def simulate_closed(service, connection_id, sock) :
    sbrk1 = create_object (service)
    sbrk1['connection_id'] = connection_id

    sbrk1['tcp_state'] = "TCP_CLOSED"

    sbrk1['tcp_total_packets'] = 20
    sbrk1['tcp_c2s_bytes'] = 21
    sbrk1['tcp_s2c_bytes'] = 32
    sbrk1['tcp_total_bytes'] = sbrk1['tcp_c2s_bytes'] + sbrk1['tcp_s2c_bytes']
    sbrk1['tcp_tiny_packets'] = 0
    sbrk1['tcp_paws_packets'] = 0
    sbrk1['tcp_retransmitted_packets'] = 0
    sbrk1['tcp_out_of_order_packets'] = 0  
    sbrk1['tcp_zero_windows'] = 0 
    sbrk1['tcp_duplicate_acks'] = 0 

    if sbrk1['protocol'] == "DEFAULT":
        sbrk1['tcp_tiny_packets'] = 222
        sbrk1['tcp_paws_packets'] = 333
        sbrk1['tcp_retransmitted_packets'] = 444
        sbrk1['tcp_out_of_order_packets'] =555 
        sbrk1['tcp_zero_windows'] = 666 
        sbrk1['tcp_duplicate_acks'] = 777 

        sbrk1['default_exchange_size'] = 1024
        sbrk1['default_server_latency'] = 497 

    else:
        sbrk1 = reset (sbrk1)

    time.sleep(12)
    now_secs = int(time.time())
    sbrk1['@timestamp'] = now_secs
    sock.send(json.dumps(sbrk1))

def simulate_reset(service, connection_id, tcp_reset_type, reset_type, sock) :
    sbrk1 = create_object (service)
    sbrk1 = reset (sbrk1)
    sbrk1['connection_id'] = connection_id

    if sbrk1['protocol'] == "HTTP":   
        sbrk1 = fullfil_sbreakdown (sbrk1, connection_id, 0, 'GET')
        sbrk1['http_state'] = reset_type


    elif sbrk1['protocol'] == "MYSQL":   
        sbrk1 = fullfil_sbreakdown (sbrk1, connection_id, 0, 'SELECT')
        sbrk1['mysql_state'] = reset_type

    sbrk1['tcp_state'] = tcp_reset_type

    now_secs = int(time.time())
    sbrk1['@timestamp'] = now_secs
    sock.send(json.dumps(sbrk1))

def http_normal_simulator (service):
    sock = context.socket(zmq.PUSH)
    sock.connect("tcp://%s:%s" % (srv_ip, srv_port))
    while True:
        for status_code in http_status_list :
            for method in http_method_list :
                method2 = method
                connection_id = simulate_connected (service, sock)
                if connection_id > 0 :
                    simulate_exchanging(service, connection_id, status_code, method2, sock)
                simulate_closed (service, connection_id, sock)

def http_reset_simulator (service) :
    sock = context.socket(zmq.PUSH)
    sock.connect("tcp://%s:%s" % (srv_ip, srv_port))
    while True:
        for http_reset_type in http_reset_list :
            time.sleep(18)
            connection_id = simulate_connected (service, sock)
            if connection_id > 0 :
                simulate_reset(service, connection_id, "TCP_RESET_TYPE3", http_reset_type, sock)

            connection_id = simulate_connected (service, sock)
            if connection_id > 0 :
                simulate_reset(service, connection_id, "TCP_RESET_TYPE4", http_reset_type, sock)

def mysql_normal_simulator (service):
    sock = context.socket(zmq.PUSH)
    sock.connect("tcp://%s:%s" % (srv_ip, srv_port))
    while True:
        for status_code in mysql_status_list :
            time.sleep(12)
            for st in mysql_statements:
                connection_id = simulate_connected (service, sock)
                if connection_id > 0 :
                    simulate_exchanging(service, connection_id, status_code, '', sock)
                simulate_closed (service, connection_id, sock)

def mysql_reset_simulator (service) :
    sock = context.socket(zmq.PUSH)
    sock.connect("tcp://%s:%s" % (srv_ip, srv_port))
    while True:
        for mysql_reset_type in mysql_reset_list :
            time.sleep(18)
            connection_id = simulate_connected (service, sock)
            if connection_id > 0 :
                simulate_reset(service, connection_id, "TCP_RESET_TYPE3", mysql_reset_type, sock)

            connection_id = simulate_connected (service, sock)
            if connection_id > 0 :
                simulate_reset(service, connection_id, "TCP_RESET_TYPE4", mysql_reset_type, sock)

def simulator (service):

    threading.Thread(target = simulate_aborted, args = (service,)).start()

    if service['protocol'] == 'HTTP' :
        threading.Thread(target = http_normal_simulator, args = (service,)).start()
        threading.Thread(target = http_reset_simulator, args = (service,)).start()

    if service['protocol'] == 'MYSQL' :
        threading.Thread(target = mysql_normal_simulator, args = (service,)).start()
        threading.Thread(target = mysql_reset_simulator, args = (service,)).start()

Watcher()
#threading.Thread(target = simulator, args = (s0,)).start()
#threading.Thread(target = simulator, args = (s1,)).start()
#threading.Thread(target = simulator, args = (s2,)).start()
simulator (s0)
simulator (s1)
simulator (s2)

