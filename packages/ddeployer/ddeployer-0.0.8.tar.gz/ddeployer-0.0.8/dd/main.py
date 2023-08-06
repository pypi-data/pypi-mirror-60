#!/usr/bin/env python
#encoding:utf-8

import os
import sys
import time
import dd 
from dd.daemon import Daemon
 
class DdServiceDaemon(Daemon):
    def run(self,port):
        sys.stdout.write('Daemon started with pid %s，port is %s\n'%(os.getpid(),port))
        while True:
            ddService = os.popen('ps -fe | grep "%s" | grep -v "grep" | wc -l'%(dd.__serverName__)).read().strip()
            #筛选出进程中含有tomcat且不含有grep，计算出现行数。修改上面的进程监控语句以适应其他应用需求
            if (ddService == '0'):
                os.system('/usr/local/bin/%s -p %s'%(dd.__serverName__,port))
                sys.stdout.write('%sd Daemon Alive! %s\n'%(dd.__daemonName__, time.ctime()))
                sys.stdout.flush() 
            time.sleep(5)
    def stop(self):
        super(DdServiceDaemon, self).stop()  
        os.system('pkill -f %s'%(dd.__serverName__))       

def run():
    PIDFILE = '/tmp/daemon-%s.pid'%(dd.__daemonName__)
    LOG = '/tmp/daemon-%s.log'%(dd.__daemonName__)
    daemon = DdServiceDaemon(pidfile=PIDFILE, stdout=LOG, stderr=LOG)
 
    if len(sys.argv) < 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)
    if 'start' == sys.argv[1]:
        port = 8866
        if len(sys.argv) == 3:
            port = sys.argv[2]
        daemon.start(port)
    elif 'stop' == sys.argv[1]:
        daemon.stop()
    elif 'restart' == sys.argv[1]:
        daemon.restart()
    elif 'kill' == sys.argv[1]:
        daemon.kill()
    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)


 
if __name__ == '__main__':
    run()
  