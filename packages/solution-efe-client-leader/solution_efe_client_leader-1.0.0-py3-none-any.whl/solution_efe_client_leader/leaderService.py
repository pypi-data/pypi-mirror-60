import socket
import json
from solution_efe_config import configConstants

CLIENT_LEADER=configConstants.CLIENTS['leader']

def leaderServiceProfileById(data):
    try:
        event = {'event':'leader-service-profile-by-id','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_LEADER['host'], CLIENT_LEADER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}