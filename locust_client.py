from gevent import socket
from locust import Locust,events,TaskSet

import logging,time


class SocketClient(object):

    def __init__(self):
        self.__socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)


    def __connect(self,ip_address,port):
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
            return True
        except BaseException as t_e:
            return False

    def __hanging_action(self):
        start_time=time.time()
        msg=self.__socket.recv(400)

        if len(msg)>=200:
            events.request_success.fire(
                request_type='recv',
                name='Recieving Data',
                response_time=(time.time()-start_time)*1000,
                response_length=len(msg)
            )
        else:
            events.request_failure.fire(
                request_type='recv',
                name='Recieving Data',
                response_time=(time.time()-start_time)*1000,
                exception='server closed'
            )

        return False

    def action(self,ip_address,port):

        try:
            while not self.__connect(ip_address,port):
                pass

        except OSError as o_e:
            # cur_locust_instance='SocketClient:{sock}, connecting to \
            #     {ip}:{port} \
            #     OSError occured client shutting down, trying to \
            #     reconnect'.format(
            #         sock=str(self),
            #         ip=self.__ip_address,
            #         port=self.__port
            # )
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
            # cur_locust_instance='SocketClient:{sock}, connection established \
            #     {ip}:{port} \
            #     OSError occured client hanging up, trying to \
            #     stop'.format(
            #         sock=str(self),
            #         ip=self.__ip_address,
            #         port=self.__port
            # )
            events.locust_error.fire(
                locust_instance='Hanging Up processing',
                exception=o_e,
                tb=sys.exec_info()[2]
            )
            self.stop()
            return

    def stop(self):
        self.__socket.close()


class SocketLocust(Locust):

    def __init__(self,*args,**kwargs):
        super(SocketLocust,self).__init__(*args,**kwargs)

        self.host='192.168.130.14'
        self.port=8081
        self.client=SocketClient()

    class task_set(TaskSet):
        def on_start(self):
            self.client.action(self.locust.host,self.locust.port)

        def on_stop(self):
            self.client.stop()
