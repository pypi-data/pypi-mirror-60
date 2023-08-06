# -*- coding: utf-8 -*-

from flask import Flask,request,abort # 引用flask库

import os
import time
import sys, getopt
from dd.mylog import TNLog
import dd


logger = TNLog()
print(__name__)
app= Flask(__name__)
app.config.update(DEBUG=True)

# 定义路由
@app.route('/')  
def hello_world():
    out = os.popen('docker info').read() 
    return out

@app.route('/docker/Info')
def getDockerInfo():
    out = os.popen('docker info').read() 
    return out

@app.route('/docker/deploy',methods=['POST'])
def deploy():
    if request.method == 'POST':
        image_name = request.form['image_name']
        run_name = request.form['run_name']
        port = request.form['port']
        other = request.form['other']
        loginfo = ''
        
        cmd = 'docker pull %s'%(image_name)
        os.popen(cmd)
        loginfo+=cmd+'\n'
        
        cmd = 'docker stop %s'%(run_name)
        loginfo+=cmd+'\n'
        print(os.popen(cmd).read())
        
        cmd = 'docker rm %s'%(run_name)
        loginfo+=cmd+'\n'
        print(os.popen(cmd).read())
        
        cmd = 'docker run -d --restart=always --name=%s -p %s %s %s'%(run_name,port,other,image_name)
        print(os.popen(cmd).read())
        loginfo+=cmd+'\n'
        logger.info(loginfo)
        cmd = "docker ps |grep '%s'"%(run_name)
        ret = os.popen(cmd).read()
        print(ret)
        if ret == '':
            return '0'
        else:    
            return '1'
         
    

@app.route('/docker/login',methods=['POST'])
def dockerLogin():
    if request.method == 'POST':
        user = request.form['u']
        pwd = request.form['p']
        host = request.form['host']
        outs = os.popen('docker login -u %s -p %s %s' %(user,pwd,host)).readlines()  
        is_successful = False      
        for l in outs:
            print(l)
            if l.startswith('Login Succeeded'):
                is_successful=True
                return '1'
        if not is_successful:        
            return '0'        
        


def getPort():
    usage = ''' 
    usage:
    python3 -m dd [-v | -h | -p <port>]
    ddService [-v | -h | -p <port>]
    '''
    port = 8866
    argv = sys.argv[1:]    
    try:
        opts, argvs = getopt.getopt(argv,"p:hv",["port=","help","version"])
    except getopt.GetoptError:
        print("parameter format error")
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
        elif opt == '-v':
            print(dd.__version__)
            sys.exit()
    return port 


def main():    
    app.run(host='0.0.0.0',port=getPort(),threaded=True,debug=False) # 开启调试模式，程序访问端口为8080



if __name__=="__main__":
    #main()
    if(not os.path.exists('log')):
        os.mkdir('log')
    #logger.info("info")
    app.run(host='0.0.0.0',debug=True,port=getPort(),threaded=True) # 开启调试模式，程序访问端口为8080
    #http_server = WSGIServer(('', 5001), app)
    #http_server.serve_forever()



