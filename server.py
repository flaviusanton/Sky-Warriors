#!/usr/bin/env python

import sys, socket, select, random
try:
   import cPickle as pickle
except:
   import pickle

MAXCL=5
MAXS=4096
pW=76
pH=48
sW=1024
sH=768

if len(sys.argv)!=2:
    sys.exit(sys.argv[0][2:]+' port')

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', int(sys.argv[1])))
sock.listen(MAXCL)
sock.setblocking(0)

conn={}
epoll=select.epoll()
epoll.register(sock.fileno(), select.EPOLLIN)
random.seed()
nrP=0
players=[]

try:
    while True:
        ev=epoll.poll(1)
        for n, e in ev:
            if n==sock.fileno():
                newsock, addr=sock.accept()
                newsock.setblocking(0)
                conn[newsock.fileno()]=newsock
                epoll.register(newsock.fileno(), select.EPOLLIN)
                nrP=nrP+1
                rX=random.randint(pW/2, sW-pW/2)
                rY=random.randint(pH/2, sH-pH/2)
                rRt=random.randrange(0, 35, 10)

                # a lil hardcoding here, will fix
                if nrP == 1:
                    rX = 500
                    rY = 500
                    rRt = 10.0
                l=[0, newsock.fileno(), rX, rY, float(rRt), 'img'+str(nrP)+'.png']
                s = pickle.dumps(l)
                newsock.sendall(s)

                if len(players)==0:
                    l[5]='img1.png'
                    players.append(l)
                else:
                    for i in range(0, len(players)):
                        print 'i= '+str(i)
                        if not players[i]:
                            l[5]='img'+str(i)+'.png'
                            players[i]=l
                            #print l
                            break
                    else:
                        players.append(l)
                #s=pickle.dumps(players)
                #newsock.sendall(s)
                #tip0, ID1, x2, y3, rot4e, path5
                p=''
                p=pickle.dumps(l)
                for k in conn.keys():
                    if k!=n:
                        try:
                            conn[k].sendall(p)
                        except:
                            pass
            elif e & select.EPOLLIN:
                try:
                    s=conn[n].recv(MAXS)
                except:
                    pass
                if s:
                    #broadcast
                    if s[:4]!='QUIT':
                        for k in conn.keys():
                            if k!=n:
                                try:
                                    conn[k].sendall(s)
                                except:
                                    pass
                    else:
                        print 'exit: '+s
                        l=int(s[-1:])
                        for i in range(len(players)):
                            if players[i][1]==l:
                                nrP=nrP-1
                                players.remove(players[i])
                                l=[-1, l]
                                p=''
                                p=pickle.dumps(l)
                                for k in conn.keys():
                                    if k!=n:
                                        try:
                                            conn[k].sendall(p)
                                        except:
                                            pass
                                epoll.unregister(n)
                                conn[n].close()
                                del conn[n]
    # TODO 
     #       if e & select.EPOLLHUP:
      #          for i in range(len(players)):
       #             if players[i][1]==
        #        nrP=nrP-1
         #       print nrP
          #      l=[-1, n]
           #     p=''
            #    p=pickle.dumps(l)
             #   for k in conn.keys():
              #          if k!=n:
               #             try:
                #                conn[k].sendall(p)
                 #           except:
                  #              pass
           #     epoll.unregister(n)
            #    conn[n].close()
             #   del conn[n]
finally:
    epoll.unregister(sock.fileno())
    epoll.close()
    sock.close()
