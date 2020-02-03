import socket
import pickle
import sys
import os
import random
from threading import Thread
from socketserver import ThreadingMixIn
sys.path.append("../")
from common import Hdr, Msg, sharedKey, send_file, recv_file, send_data, recv_data, PubKey
import settings

# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print("[+] New server socket thread started for " + ip + ":" + str(port))
 
    def run(self): 

        # Get the 3 keys from the client
        client_pub_a = pickle.loads(recv_data(conn)).get_msg()
        client_pub_b  = pickle.loads(recv_data(conn)).get_msg()
        client_pub_c = pickle.loads(recv_data(conn)).get_msg()

        # Generate private keys and public keys with same large prime and
        # primitive root
        private_a_server = random.randint(1, client_pub_a.q - 1)
        server_pub_a = PubKey(client_pub_a.q, client_pub_a.alpha)
        server_pub_a.gen_pub_key(private_a_server)

        private_b_server = random.randint(1, client_pub_b.q - 1)
        server_pub_b = PubKey(client_pub_b.q, client_pub_b.alpha)
        server_pub_b.gen_pub_key(private_b_server)

        private_c_server = random.randint(1, client_pub_c.q - 1)
        server_pub_c = PubKey(client_pub_c.q, client_pub_c.alpha)
        server_pub_c.gen_pub_key(private_c_server)

        # Generate shared keys
        shared_a = sharedKey(client_pub_a, private_a_server)
        shared_b = sharedKey(client_pub_b, private_b_server)
        shared_c = sharedKey(client_pub_c, private_c_server)

        # Send the 3 public keys of server to client
        hdr = Hdr(10, settings.TCP_PORT, self.port)
        msg_a = Msg(hdr, server_pub_a)
        msg_b = Msg(hdr, server_pub_b)
        msg_c = Msg(hdr, server_pub_c)

        send_data(conn, pickle.dumps(msg_a))
        send_data(conn, pickle.dumps(msg_b))
        send_data(conn, pickle.dumps(msg_c))

        while True: # serve the client according to the requests arrived
            msg = pickle.loads(recv_data(conn))

            if msg.type() == "REQSERV":
                file_name = msg.get_msg()
                # now check if this file is present in the file system
                if os.path.isfile('data/' + file_name):    # Check if file available in the server
                    send_file(conn,
                              'data/' + file_name,
                              settings.TCP_PORT,
                              self.port,
                              [shared_a, shared_b, shared_c]
                              )
                else:
                    # send disconnect
                    hdr = Hdr(50, settings.TCP_PORT, self.port)
                    msg_dc = Msg(hdr, "File not present in server")
                    send_data(conn, pickle.dumps(msg_dc))
                    break

            if msg.type() == "DISCONNECT":
                # Disconnect this client from the server
                print("Client disconnected from the server")
                break

if __name__ == "__main__":
    BUFFER_SIZE = 1024 

    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    tcpServer.bind((settings.TCP_IP, settings.TCP_PORT)) 
    threads = [] 
     
    while True: 
        tcpServer.listen(4) 
        print("Multithreaded Python server : Waiting for connections from TCP clients...")
        (conn, (ip,port)) = tcpServer.accept() 
        newthread = ClientThread(ip,port) 
        newthread.start() 
        threads.append(newthread) 
     
    for t in threads: 
        t.join()
