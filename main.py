import json
import socket
import sys
import io
import threading
import settings
import time


class server_manager():


    requests={}

    def start_server(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('37.187.55.53', 1323))
        sock.listen(5)


        while True:

            conn,addr=sock.accept()
            thr = threading.Thread(target=self.request_handler, args=(conn, addr))
            thr.start()


    def get_responce(self,requset:str):
        start=requset.find('Host:')
        data = b''
        if start!=-1
            end=requset.find('/n',__start=start)

            host=requset[start+5:end]

            port=host.find(':')

            if port!=-1:
                host=host[:port]
                port=host[port+1:]
            else:
                port=80

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = (host, port)

            sock.connect(server_address)
            sock.sendall(requset)

            while True:
                temp=sock.recv(4096)
                if temp:
                    data+=temp
                else:break

            sock.close()
        return data







    def handle(self,conn,addr):

        conn.settimeout(settings.socket_timeout)
        json_data=json.loads(conn.recv(4000).decode(),encoding='utf-8')
        conn.settimeout(None)
        responce_fragments=[]


        #ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        #ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

        if json_data['op']=='send_req_data':

            conn.settimeout(settings.socket_timeout)
            conn.sendall('ack')
            conn.settimeout(None)

            #veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ ფრაგმენტს
            if self.requests[json_data['req_id']]:
                self.requests[json_data['req_id']].append(json_data['data'])
            else:
                self.requests[json_data['req_id']]=[json_data['data']]
            conn.close()

        #ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        #თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        #ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        #ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

        elif json_data['op']=='receive_fr_count':

            fragment_list=self.requests['req_id']
            conn.settimeout(settings.socket_timeout)
            conn.sendall(str(len(fragment_list)).encode())
            conn.settimeout(None)
            conn.close()







        #თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op']=='receive_fr_data':

            fragment_list=self.requests['req_id']
            fragment_id=self.requests['fr_index']

            resp_fr_data=self.requests[json_data['res_id']]['responces'][fragment_id]


            conn.settimeout(settings.socket_timeout)
            conn.sendall(resp_fr_data)
            conn.settimeout(None)
            conn.close()

















