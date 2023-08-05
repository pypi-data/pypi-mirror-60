import socket
import json
from solution_efe_config import configConstants

CLIENT_USER=configConstants.CLIENTS['user']

def userServiceLogin(data):
    try:
        event = {'event':'user-service-login','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}

def userServiceLoginMember(data):
    try:
        event = {'event':'user-service-login-member','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}

def userServiceUpdatePasswordMember(data):
    try:
        event = {'event':'user-service-update-password-member','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}

def userServiceUpdatePasswordLeader(data):
    try:
        event = {'event':'user-service-update-password-leader','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}

def userServiceCodeValidate(data):
    try:
        event = {'event':'user-service-code-validate','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}

def userServiceUpdatePasswordCode(data):
    try:
        event = {'event':'user-service-update-password-code','data': data}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return response
    except Exception as e:
        return {'code': 500,'status': False,'data':str(e)}