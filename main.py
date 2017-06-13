import json
import socket
import sys
import io
import threading
import settings
import time
import textwrap

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
        start=requset.find('Host:')
        data = b''
        if start!=-1:
            end=requset.find('\r\n',start)

            host=requset[start+5:end]

            port=host.find(':')

            if port!=-1:
                ahost=host[:port]
                aport=host[port+1:]
                host=ahost
                port=int(port)
                ss=6
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


        return textwrap.wrap(data, 4000)







    def handle(self,conn,addr):

        conn.settimeout(settings.socket_timeout)
        data=conn.recv(4000).decode()
        json_data=json.loads(data )
        conn.settimeout(None)
        responce_fragments=[]


        #ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        #ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

        if json_data['op']=='send_req_data':

            conn.settimeout(settings.socket_timeout)
            conn.sendall('ack'.encode())
            conn.settimeout(None)

            #veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს

            print(json_data)
            print(self.requests)

            self.requests[json_data['request_id']]={'request':json_data['data']}
            self.requests[json_data['request_id']]['responce']=[]
            conn.close()

        #ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        #თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        #ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        #ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

        elif json_data['op']=='receive_fr_count':

            fragment_list=self.requests[json_data['request_id']]['responce']
            conn.settimeout(settings.socket_timeout)
            conn.sendall(str(len(fragment_list)).encode())
            conn.settimeout(None)
            conn.close()
            request=self.requests[json_data['request_id']]['request']



            self.requests[json_data['request_id']]['responce']+=self.get_responce(request)








        #თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op']=='receive_fr_data':

            fragment_list=self.requests[json_data['request_id']]
            fragment_id=self.requests['fr_index']

            resp_fr_data=self.requests[json_data['res_id']]['responces'][fragment_id]


            conn.settimeout(settings.socket_timeout)
            conn.sendall(resp_fr_data)
            conn.settimeout(None)
            conn.close()

















def server():
    a=server_manager()
    a.start_server()
if __name__ == "__main__":
    server()



