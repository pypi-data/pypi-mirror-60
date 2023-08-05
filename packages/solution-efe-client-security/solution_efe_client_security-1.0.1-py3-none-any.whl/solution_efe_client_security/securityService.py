import socket
import json
from solution_efe_config import configConstants

CLIENT_SECURITY=configConstants.CLIENTS['security']

def securityServiceTokenValid(token):
    try:
        event = {'event':'security-service-token-validate','data': {'token':token}}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_SECURITY['host'], CLIENT_SECURITY['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response 
    except Exception as e:
        return { 'code' : 500 , 'status': False,'data':str(e)}

def securityServiceTokenGenerate(data):
    try:
        event = {'event':'security-service-token-generate','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_SECURITY['host'], CLIENT_SECURITY['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return { 'code' : 500 , 'status': False,'data':str(e)}

def securityServiceTokenDecode(data):
    try:
        event = {'event':'security-service-token-decode','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_SECURITY['host'], CLIENT_SECURITY['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return { 'code' : 500 , 'status': False,'data':str(e)}