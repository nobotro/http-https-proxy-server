import base64
import datetime
import json
import pickle
import socket
import sys
import io
import threading
from struct import unpack
from urllib.parse import urlparse

import settings
import time
import textwrap
import email
import pprint
from io import StringIO
import gzip
import logging

# C:\\Users\\Administrator\\PycharmProjects\\geocell_proxy_server\logs\\
logging.basicConfig(filename='server.log', format='%(asctime)s %(message)s', level=logging.DEBUG)


class server_manager():
    requests = {}
    https_sesions = {}

    requests_counter = 0
    thread_lock = threading.Lock()

    def clean(self):

        while True:

            dell = []
            for i in self.https_sesions:

                if (datetime.datetime.now() - self.https_sesions[i]['stamp']).total_seconds() > settings.clean_time:
                    try:

                        self.https_sesions[i]['sesion'].close()

                    except:
                        pass

                    try:
                        dell.append(i)
                    except:
                        pass

                    try:
                        del (self.requests[i])
                    except:
                        pass

            for i in dell:
                try:
                    del (self.https_sesions[i])
                except:
                    pass

            time.sleep(7)

    def get_next_request_count(self, *args):

        self.thread_lock.acquire()
        res = self.requests_counter + 1
        self.requests_counter = res
        self.thread_lock.release()
        return res


    def port_range_mapper(self,range_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind((settings.remote_server_ip,range_port))
        while True:
            try:

                data, addr = sock.recvfrom(65507)

                thr = threading.Thread(target=self.handle, args=(data, addr, sock))
                thr.daemon = True
                thr.start()
            except:
                pass

    def start_server(self):

        print('[*] start proxy server at ip {} and port {}'.format(settings.remote_server_ip,'-ranged port-'))
        print('[*] protocol http/https')
        print('[*] socket protocol udp')
        print('[*] time:' + str(datetime.datetime.now()))

        thr2 = threading.Thread(target=self.clean)

        thr2.start()

        for i in settings.remote_server_port_range:
            thr2 = threading.Thread(target=self.port_range_mapper,args=(i,))

            thr2.start()









                # ბინარი სტრინგი მოდის თავიდან და არა რექვესთი

    def get_responce(self, requset, sesion=None, https=False, request_id=None):

        data = b''
        pats=[]
        sock = ''
        try:
            if not https:

                try:
                    _, headers = requset.split('\r\n', 1)
                except Exception as e:
                    logging.exception('message')
                    return

                    # print('sgsg erori')
                    # print(requset)
                    # print(sesion)

                # construct a message from the request string
                message = email.message_from_file(StringIO(headers))

                # construct a dictionary containing the headers
                headers = dict(message.items())
                headers['method'], headers['path'], headers['http-version'] = _.split()

                url = urlparse(headers['path'])

                requset = requset.replace(headers['path'], headers['path'].replace(url.scheme + '://' + url.netloc, ''))
                host = headers['Host']
                lr = host.split(':')
                host = lr[0]
                if len(lr) == 2:
                    port = int(lr[1])

                else:
                    port = 80

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect the socket to the port where the server is listening
                server_address = (host, port)
                # print(server_address)
                try:
                    sock.connect(server_address)
                    sock.sendall(requset.encode())
                except Exception as e:
                    sock.close()
                    logging.exception('message')
                    return

                while True:

                    try:
                        temp=b''
                        sock.settimeout(0.1)
                        temp = sock.recv(1)
                        sock.settimeout(None)
                        if len(temp) != 1: break
                        temp += sock.recv(65000)
                        data += temp



                    except Exception as e:

                        if sock:

                            try:

                                sock.settimeout(None)

                                sock.close()

                            except Exception as e:

                                sock.close()

                                logging.exception("message")

                                logging.info('tipi' + str(sock) + ' :' + str(type(sock)))

                                print('tipi' + str(sock) + ' :' + str(type(sock)))

                        break
                    except socket.timeout:

                            print('abababababab')

                            break




            else:

                # print('ses'+str(sesion))

                sock = sesion

                requset = base64.decodebytes(requset.encode())

                sock.sendall(requset)

                timeout = settings.global_timeout

                recchaci = b'\x14\x03'

                recalert = b'\x15\x03'

                rechand = b'\x16\x03'

                datarec = b'\x17\x03'

                patterns = [recchaci, recalert, rechand, datarec]
                timeout=0.1
                dataindex=0
                # otxive davdzebnot da amovigot bolos wina end() pozicia
                if requset.startswith(datarec):timeout=0.2
                data =sock.recv(65000)

                while True:

                    try:


                            if not dataindex:
                                dataindex = data.rfind(datarec)

                            if dataindex != -1:
                                timeout = 0.5

                            temp = b''
                            sock.settimeout(timeout)
                            temp = sock.recv(1)
                            sock.settimeout(None)
                            if len(temp) != 1:
                                sock.settimeout(None)
                                break
                            temp += sock.recv(65000)
                            data += temp

                    except socket.timeout:


                            break



                    except Exception as e:

                            if sock:

                                try:

                                    sock.settimeout(None)

                                    sock.close()

                                except Exception as e:

                                    sock.close()

                                    logging.exception("message")

                                    logging.info('tipi' + str(sock) + ' :' + str(type(sock)))

                                    print('tipi' + str(sock) + ' :' + str(type(sock)))

                            break

                for pat in patterns:
                    pats.append(data.rfind(pat))
                print('')

                info = [data[i:i + settings.max_fragment_size] for i in

                        range(0, len(data), settings.max_fragment_size)]

                return info,pats

            # data = gzip.compress(data, compresslevel=6)
            info = [data[i:i + settings.max_fragment_size] for i in range(0, len(data), settings.max_fragment_size)]
            return info
        except:
            return b''

    def handle(self, data, addr, conn):

        data = data.decode()
        json_data = json.loads(data)

        # print(json_data)


        responce_fragments = []

        # ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        # ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

        if json_data['op'] == 'send_req_data':

            if 'request_id' not in json_data.keys():
                request_id = str(self.get_next_request_count())
                print('{} ,-> movida reqvestis data hosti {} da porti {} ,biji {} , zoma {} ,'.format(request_id,json_data['host'],json_data['port'],json_data['biji'],len(json_data['data'])))
                if json_data['port'] and json_data['host']:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    server_address = (json_data['host'], json_data['port'])
                    sock.settimeout(settings.global_timeout)
                    sock.connect(server_address)
                    sock.settimeout(None)
                    self.https_sesions[request_id] = {'sesion': sock,
                                                      'stamp': datetime.datetime.now()}


            else:
                request_id = json_data['request_id']
                print('{} ,-> movida reqvestis data ,biji {} , zoma {}'.format(request_id,json_data['biji'],len(json_data['data'])))


            # logging.info("received request with id: "+str(request_id))

            self.requests[request_id] = {'request': json_data['data']}
            self.requests[request_id]['responce'] = []

            resp = json.dumps({'request_id': request_id}, ensure_ascii=False).encode()

            conn.sendto(resp, addr)
            print('{} ,<- gavagzavne reqvestis dataze acki ,biji {} , zoma {}'.format(request_id,json_data['biji'], len(json_data['data'])))


            # veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს




        # ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        # თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        # ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        # ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

        elif json_data['op'] == 'receive_fr_count':

            # თუ უკვე რესპონსი გვაქვს ამ რექვესთის,მეორედ რომ აღარ ამოვიღოთ
            if len(self.requests[json_data['request_id']]['responce']) <= 0:

                request = self.requests[json_data['request_id']]['request']

                del (self.requests[json_data['request_id']]['request'])
                self.requests[json_data['request_id']]['responce'] = []
                res = self.get_responce(request)


                if res:
                    self.requests[json_data['request_id']]['responce'] += res

                    self.requests[json_data['request_id']]['responce'][0] = ''
                    fragment_list = self.requests[json_data['request_id']]['responce']
                    # print('receive_fragment_count:' + str(len(fragment_list)))
                    ffragment = base64.encodebytes(res[0]).decode()
                    json_responce = json.dumps({'len': len(fragment_list), 'fragment': ffragment},
                                               ensure_ascii=False).encode()



                    #
                    conn.sendto(json_responce, addr)

                else:
                    conn.sendto(str('0').encode(), addr)
                    return


        # თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op'] == 'receive_fr_data':

            if 'action' in json_data.keys():

                print('{} ,-> movida fragmentis washlis brdzaneba, biji {} ,indeqsi {}'.format(json_data['request_id'],json_data['biji'],json_data['fr_index']))

                # დასაფიქსია
                try:
                    self.requests[json_data['request_id']]['responce'][json_data['fr_index']] = ''
                except:
                    logging.error('imena is erori----------------' + str(json_data))
                    return


            else:

                print('{} ,-> movida fragmentis migebis brdzaneba , biji {} ,indeqsi {}'.format(json_data['request_id'],json_data['biji'],json_data['fr_index']))


                # logging.info("fragment request with id: " + str(json_data['request_id'])+' and fragment id: '+str(json_data['fr_index']))



                resp_fr_data = ''
                try:
                    resp_fr_data = self.requests[json_data['request_id']]['responce'][json_data['fr_index']]

                    conn.sendto(resp_fr_data, addr)
                    print('{} ,<- gavagzavne fragmenti ,indeqsi {} ,biji {} , zoma {}'.format(json_data['request_id'],json_data['fr_index'],json_data['biji'],len(resp_fr_data)))


                except Exception as e:
                    logging.exception('message')
                    conn.sendto(b'', addr)
                    print('+++++++is erori ' + str(json_data))

                # logging.info("gaigzavna: " + str(json_data['request_id']) + ' and fragment id: ' + str(json_data['fr_index']))


        elif json_data['op'] == 'https_receive_fr_count':

            try:

                request = self.requests[json_data['request_id']]['request']
                print('{} ,-> movida count(fragmentis) migebis brdzaneba ,biji {} '.format(json_data['request_id'],json_data['biji']))

                if request == 'already_received':

                    conn.sendto(str(len(self.requests[json_data['request_id']]['responce'])).encode(), addr)
                    return
                else:
                    self.requests[json_data['request_id']]['request'] = 'already_received'


                if json_data['request_id'] in self.https_sesions.keys():

                    sesion = self.https_sesions[json_data['request_id']]['sesion']

                    self.requests[json_data['request_id']]['responce'] = []
                    if sesion:
                        nt=datetime.datetime.now()
                        res,pats = self.get_responce(request, sesion=sesion, https=True, request_id=json_data['request_id'])
                        nt2=datetime.datetime.now()
                        print('{} ,- mivige data web serverisgan pat{} ,zoma {}, biji {} ,dro {}'.format(json_data['request_id'],pats,len(res),json_data['biji'],(nt2-nt).total_seconds()))

                    else:
                        raise Exception('not sesion exception')
                    if res:
                        self.requests[json_data['request_id']]['responce'] += res
                        self.requests[json_data['request_id']]['responce'][0]=''
                        fragment_list = self.requests[json_data['request_id']]['responce']
                        # print('receive_fragment_count:' + str(len(fragment_list)))
                        ffragment = base64.encodebytes(res[0]).decode()
                        json_responce = json.dumps({'len': len(fragment_list), 'fragment': ffragment},
                                                ensure_ascii=False).encode()


                        #
                        conn.sendto(json_responce, addr)


                    #     fragment_list = self.requests[json_data['request_id']]['responce']
                    #     # print('receive_fragment_count:' + str(len(fragment_list)))
                    #     conn.sendto(str(len(fragment_list)).encode(), addr)
                    # else:
                    else:

                        sesion.close()
                        raise Exception('responsi carielia erori')







                else:
                    raise Exception('sesia araa erori')



            except:
                logging.exception('message')
                conn.sendto('0'.encode(), addr)
                return



        elif json_data['op'] == 'clean':
            if json_data['request_id'] in self.requests:
                del (self.requests[json_data['request_id']])
            if json_data['request_id'] in self.https_sesions:
                self.https_sesions[json_data['request_id']]['sesion'].close()


def server():
    a = server_manager()

    a.start_server()


if __name__ == "__main__":
    server()



