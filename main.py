import json
import socket
import sys
import io
import threading
import settings
import time
import textwrap
import email
import pprint
from io import StringIO
class server_manager():


    requests={}

    def start_server(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('37.187.55.53', 1327))
        sock.listen(5)


        while True:

            conn,addr=sock.accept()
            thr = threading.Thread(target=self.handle, args=(conn, addr))
            thr.start()






    def get_responce(self,requset:str):

        data=b''
        try:
            _, headers =requset.split('\r\n', 1)
        except:
            print('sgsg erori')

        # construct a message from the request string
        message = email.message_from_file(StringIO(headers))

        # construct a dictionary containing the headers
        headers = dict(message.items())
        headers['method'], headers['path'], headers['http-version'] = _.split()

        if headers['method']!='CONNECT':
            host=headers['Host']
            lr=host.split(':')
            host=lr[0]
            if len(lr)==2:
                port=int(lr[1])

            else:port=80








            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = (host,port)
            print(server_address)
            try:
             sock.connect(server_address)
            except:
                print('shsh')
            sock.sendall(requset.encode())

            while True:
                temp=None
                try:
                    sock.settimeout(3)
                    temp = sock.recv(4096)
                    sock.settimeout(None)
                except:
                    sock.close()

                    break


                if temp:
                    data+=temp
                else:
                    sock.close()
                    break



        info = [data[i:i + 4000] for i in range(0, len(data), 4000)]
        return info







    def handle(self,conn,addr):

        conn.settimeout(settings.socket_timeout)
        data=conn.recv(4000).decode()
        json_data=json.loads(data)
        print(json_data)

        conn.settimeout(None)
        responce_fragments=[]


        #ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        #ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

        if json_data['op']=='send_req_data':

            conn.settimeout(settings.socket_timeout)
            conn.sendall('ack'.encode())
            conn.settimeout(None)

            #veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს



            self.requests[json_data['request_id']]={'request':json_data['data']}
            self.requests[json_data['request_id']]['responce']=[]
            conn.close()

        #ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        #თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        #ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        #ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

        elif json_data['op']=='receive_fr_count':
            request = self.requests[json_data['request_id']]['request']

            self.requests[json_data['request_id']]['responce'] += self.get_responce(request)

            fragment_list=self.requests[json_data['request_id']]['responce']
            print('receive_fragment_count:' +str(len(fragment_list)))
            conn.settimeout(settings.socket_timeout)
            conn.sendall(str(len(fragment_list)).encode())
            conn.settimeout(None)
            conn.close()








        #თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op']=='receive_fr_data':



            resp_fr_data=self.requests[json_data['request_id']]['responce'][json_data['fr_index']]


            conn.settimeout(settings.socket_timeout)
            conn.sendall(resp_fr_data)
            conn.settimeout(None)
            conn.close()

















def server():
    a=server_manager()
    a.start_server()
if __name__ == "__main__":
    server()



