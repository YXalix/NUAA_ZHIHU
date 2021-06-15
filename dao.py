from typing import Counter
import psycopg2
from flask import Flask,request,render_template,g,jsonify
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired
import re
import time
auth = HTTPBasicAuth()

SECCRET_KEY = 'FCYXAAAA'
# 生成Token，有效时间为600min
def generate_auth_token(username,expiration=36000):
    # 第一个参数是内部私钥
    # 第二个参数是有效期
    s = Serializer(SECCRET_KEY,expires_in=expiration)
    token = s.dumps({'username': username})
    return token

# 解析token
def verify_auth_token(token):
    s = Serializer(SECCRET_KEY)
    # token 正确
    try:
        data = s.load(token)
        conn = db_connect()
        user = getuser_by_username(conn,data['username'])
        return user
    # token过期
    except SignatureExpired:
        return None
    # token错误
    except BadSignature:
        return None

def db_connect():
    conn = psycopg2.connect(database='postgres',user='myself',password='zhp@521224',host='124.70.46.225',port='26000')
    print("Connection established")
    return conn

def create_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM myusers")
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        print(row)

def add_one_question(conn,content,userid):
    cursor = conn.cursor()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(now)
    try:
        cursor.execute("INSERT INTO questions(content,authorid,time) VALUES('{content}',{authorid},'{time}')".format(content=content,authorid=userid,time=now))
        conn.commit()
        cursor.close()
        return True
    except:
        conn.rollback()
        cursor.close()
        return False

def get_all_self_questions(conn,userid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE authorid={id}".format(id=userid))
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_all_self_answers(conn,userid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM answers WHERE ansid={id}".format(id=userid))
    rows = cursor.fetchall()
    cursor.close()
    return rows  

def get_all_questions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        print(row)

def get_one_question(conn,questionID):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id={id}".format(id=questionID))
    rows = cursor.fetchall()
    cursor.close()
    return rows

def connect(conn,username,password):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM myusers WHERE username='{username}' and password='{password}'".format(username=username,password=password))
    userid = cursor.fetchone()
    cursor.close()
    return userid

def getuser_by_username(conn,username):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM myusers WHERE username='{username}'".format(username=username))
    except:
        return None
    user = cursor.fetchone()
    cursor.close()
    return user

def adduser(conn,username,password):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO myusers(username, password) VALUES('{username}','{password}')".format(username=username,password=password))
        conn.commit()
    except:
        conn.rollback()
    cursor.close()

if __name__ == "__main__":
    conn = db_connect()
    #create_db(conn)
    rows = get_one_question(conn,1)
    for row in rows:
        print(row)
    conn.close()
    