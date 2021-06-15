from flask import Flask,request,render_template,g,jsonify,flash,session,redirect,url_for
from markupsafe import escape
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired
import json
import dao
import psycopg2
app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/',methods=['POST','GET'])
def welcome():
    if 'username' in session:
        error = None
        if request.method == 'POST':
            print(request.form['content'])
            return show_question(int(request.form['content']))
        else:
            return render_template('index.html',username = session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/world')
def world(name=None):
    return render_template('world.html', name=name)

@app.route('/selfcenter')
def selfcenter():
    conn = dao.db_connect()
    user = dao.getuser_by_username(conn,session['username'])
    qsdatas = dao.get_all_self_questions(conn,user[0])
    ansdatas = dao.get_all_self_answers(conn,user[0])
    temp = []
    for item in qsdatas:
        item1 = list(item)
        item1[3] = str(item1[3])
        temp.append(item1)
    qsnum = len(qsdatas)
    ansnum = len(ansdatas)
    data = {
        'username':session['username'],
        'qsnum':qsnum,
        'ansnum':ansnum,
    }
    return render_template('selfcenter.html',data=data,questions = qsdatas,answers = ansdatas)

@app.route('/questions/<int:questionID>')
def show_question(questionID):
    conn = dao.db_connect()
    rows = dao.get_one_question(conn,questionID)
    conn.close()
    return rows[0][1]

@app.route('/qslist')
def qslist(page=1):
    conn = dao.db_connect()
    qslist = dao.get_certain_num_questions(conn,10,0)
    qsnum = dao.get_questions_num(conn)
    pagenum = int(qsnum[0] / 10)+2
    ansnums = []
    for item in qslist:
        ansnums.append(dao.get_question_answernum(conn,item[0]))
    conn.close()
    qsl = zip(qslist,ansnums)
    data = {
        'username':session['username'],
        'qsnum':qsnum,
    }
    return render_template('qslist.html',data = data,questions = qsl,pagenum=pagenum,nowpage=page)

@app.route('/qslist/<int:page>')
def qslistpage(page=1):
    conn = dao.db_connect()
    qslist = dao.get_certain_num_questions(conn,10,(page-1)*10)
    qsnum = dao.get_questions_num(conn)
    pagenum = int(qsnum[0] / 10)+2
    ansnums = []
    for item in qslist:
        ansnums.append(dao.get_question_answernum(conn,item[0]))
    conn.close()
    qsl = zip(qslist,ansnums)
    data = {
        'username':session['username'],
        'qsnum':qsnum,
    }
    return render_template('qslist.html',data = data,questions = qsl,pagenum=pagenum,nowpage=page)

@app.route('/pushquestion',methods=['POST','GET'])
def pushquestion():
    if request.method == 'POST':
        conn = dao.db_connect()
        content = request.form.get('question')
        user = dao.getuser_by_username(conn,session['username'])
        if dao.add_one_question(conn,content,user[0]):
            return render_template('questions.html',username = session['username'],msg="提问成功")
        else:
            return render_template('questions.html',username = session['username'],msg="提问失败")
    return render_template('questions.html',username = session['username'])

@auth.verify_password
def verify_password(username,password):
    conn = dao.db_connect()
    user = dao.getuser_by_username(conn,username)
    if not user:
        return False
    elif user[2] == password:
        return True
    return False

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':        
        username = request.form.get('username')
        password = request.form.get('password')
        if not verify_password(username,password):
            return render_template('login.html',msg = "用户名密码错误")
        else:
            session['username'] = request.form['username'] 
            return redirect(url_for('welcome'))
            #return render_template('index.html',{'token':token})
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        conn = dao.db_connect()
        if not all([username,password1,password2]):
            flash("参数不完整")
        elif password1 != password2:
            flash("密码不一致")
        elif dao.getuser_by_username(conn,username):
            flash("用户名重复")
        else:
            dao.adduser(conn,username,password1)
            return render_template('login.html',msg = "创建成功请登录")
    return render_template('register.html')