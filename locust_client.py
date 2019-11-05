from gevent import socket
from locust import Locust,events,TaskSet,task

import logging,time,sys


class SocketClient(object):
    '''
        Client class that implements the basic actions that locust client need
        to use. SocketClient.action() function as the entire workflow.
    '''

    def __init__(self):
        self.__socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connected=False


    def __connect(self,ip_address,port):
        '''
            Parameters:
                -ip_address: String that represents remote host's ipv4 address
                -port: An integer that represents remote host's port number
            Return:
                -Boolean value, True for successfully connection.
        '''
        start_time=time.time()
        try:
            self.__socket.connect(
                address=(ip_address,port)
            )
            events.request_success.fire(
                request_type='connect',
                name='Connecting to Server',
                response_time=(time.time()-start_time)*1000,
                response_length=0
            )
            self.connected=True
            return True
        except TimeoutError as t_e:
            return False


    def __hanging_action(self):
        '''
            Return:
                -Boolean value, False for action interrupt
        '''
        start_time=time.time()
        msg=self.__socket.recv(400)

        if len(msg)==0:
            events.request_failure.fire(
                request_type='recv',
                name='Recieving Data',
                response_time=(time.time()-start_time)*1000,
                exception='server closed'
            )
        else:
            events.request_success.fire(
                request_type='recv',
                name='Recieving Data',
                response_time=(time.time()-start_time)*1000,
                response_length=len(msg)
            )

        return False

    def action(self,ip_address,port):
        '''
            Parameters:
                -ip_address: String that represents remote host's ipv4 address
                -port: An integer that represents remote host's port number
        '''
        try:
            while not self.__connect(ip_address,port):
                pass

        except OSError as o_e:
            events.locust_error.fire(
                locust_instance='Connecting processing',
                exception=o_e,
                tb=sys.exec_info()[2]
            )
            return

        try:
            while not self.__hanging_action():
                pass
        except OSError as o_e:
            events.locust_error.fire(
                locust_instance='Hanging Up processing',
                exception=o_e,
                tb=sys.exec_info()[2]
            )
            self.stop()
            return

    def stop(self):
        self.connected=False
        self.__socket.close()



class SocketLocust(Locust):

    def __init__(self,*args,**kwargs):
        super(SocketLocust,self).__init__(*args,**kwargs)

        self.host='192.168.130.15'
        self.port=8741
        self.client=SocketClient()

    class task_set(TaskSet):
        def on_start(self):
            self.client.action(self.locust.host,self.locust.port)

        def on_stop(self):
            self.client.stop()

        @task
        def reconnect(self):
            if not self.client.connected:
                self.client.action(self.locust.host,self.locust.port)
