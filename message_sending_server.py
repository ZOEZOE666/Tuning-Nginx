from gevent.server import StreamServer
from gevent.pool import Pool
import gevent

import logging,sys


class MessageSendingServer(object):
    '''
        Server project based on stream server, each greenlet handle a request
        sending thru socket.
    '''

    def __init__(self,ip_address,port):
        self.__ip_addr=ip_address
        self.__port=port
        self.__init_logger()

        self.logger.info(
            'Initializing Message Sending Server with {adr}:{port}'.format(
                adr=ip_address,
                port=port
            )
        )


    def __init_logger(self):
        '''
            Basic configuration for logging system, make log with info, debug and
            warning level print in a readable formation.
        '''
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S'
        )
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S'
        )
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S'
        )

        self.logger=logging.getLogger(__name__)


    def handler(self,socket,address):
        '''
            Handler that take greenlet spwan to complete the server tasks. Keep
            sending message to client every second.
        '''
        current_g=gevent.getcurrent()

        self.logger.info('New connection from {adr} via greelet {c_g}'.format(
                adr=self.__ip_addr,
                c_g=current_g
                )
        )

        while True:
            try:
                gevent.sleep(1)
                socket.send(bytes(200))
                self.logger.info('Send Message to {adr}:{port}'.format(
                        adr=address[0],
                        port=address[1]
                    )
                )
            except Exception as e:
                self.logger.warning('Exception caught in handdle function.'+str(e))
                socket.close()
                gevent.kill(current_g)


    def start(self):
         '''
             Encapsulate the functions used to start up stream server, and the \
             and the situation that force to stop the server.
         '''
         pool=Pool(None)

         try:
             server=StreamServer((self.__ip_addr,self.__port),self.handler,spawn=pool)
             self.logger.info('Server Starut up successfully on {adr}:{port}'.format(
                     adr=self.__ip_addr,
                     port=self.__port
                 )
             )
             server.serve_forever()
         except Exception as e:
             self.logger.warning('Exception caught when starting up server.'+str(e))
             server.stop()


def main():
    __SERVER_ADDRESS='192.168.130.14'
    __SERVER_PORT=8081

    if len(sys.argv)==2:
        mss=MessageSendingServer(ip_address=sys.argv[1])
    if len(sys.argv)==3:
        mss=MessageSendingServer(ip_address=sys.argv[1],port=int(sys.argv[2]))
    else:
        mss=MessageSendingServer(ip_address=__SERVER_ADDRESS,port=__SERVER_PORT)
    mss.start()

if __name__=='__main__':
    main()
