# Python TCP Client A
import socket
import pickle
import random
import sys
sys.path.append("../")
from common import send_file, recv_file, sharedKey, PubKey, send_data, recv_data, Hdr, Msg
import settings

if __name__ == "__main__":
    port = settings.TCP_PORT
    host = settings.TCP_IP
    if len(sys.argv) > 1:
        host = sys.argv[1]
     
    tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    tcpClientA.connect((host, port))

    # Create 3 public keys to be shared with the server
    a, b, c = PubKey(), PubKey(), PubKey()
    private_a = random.randint(1, a.q - 1)  # Random number between 1 and a.q - 1
    private_b = random.randint(1, b.q - 1)  # Random number between 1 and b.q - 1
    private_c = random.randint(1, c.q - 1)  # Random number between 1 and c.q - 1
    a.gen_pub_key(private_a)
    b.gen_pub_key(private_b)
    c.gen_pub_key(private_c)

    # Create header for public key sharing
    hdr = Hdr(settings.PUBKEY, tcpClientA.getsockname(), port)
    msg_a = Msg(hdr, a)
    msg_b = Msg(hdr, b)
    msg_c = Msg(hdr, c)

    send_data(tcpClientA, pickle.dumps(msg_a))
    send_data(tcpClientA, pickle.dumps(msg_b))
    send_data(tcpClientA, pickle.dumps(msg_c))

    # Recieve server public keys
    server_pub_a = pickle.loads(recv_data(tcpClientA)).get_msg()
    server_pub_b = pickle.loads(recv_data(tcpClientA)).get_msg()
    server_pub_c = pickle.loads(recv_data(tcpClientA)).get_msg()

    # Generate shared keys at client
    shared_a = sharedKey(server_pub_a, private_a)
    shared_b = sharedKey(server_pub_b, private_b)
    shared_c = sharedKey(server_pub_c, private_c)

    print("Sharing of key over\n")

    print("Type the operation to be executed at the server.")
    print("Type 'help' without quotes to get the list of operations.")
    while True: # Till a disconnect is sent from client, continue conversing with server
        operation = input()
        operation = operation.split(" ")
        if operation[0] == "help":
            print("---> REQSERV <Filename> - To download file from server")
            print("---> DISCONNECT - To end the connection")

        elif operation[0] == "REQSERV":
            file_name = operation[1]
            hdr = Hdr(settings.REQSERV, tcpClientA.getsockname(), port)
            msg = Msg(hdr, file_name)
            send_data(tcpClientA, pickle.dumps(msg))
            response = recv_file(tcpClientA, file_name, [shared_a, shared_b, shared_c])
            print(response)

        elif operation[0] == "DISCONNECT":
            hdr = Hdr(settings.DISCONNECT, tcpClientA.getsockname(), port)
            msg = Msg(hdr, "Disconnect from the server")
            send_data(tcpClientA, pickle.dumps(msg))
            tcpClientA.close()
            print("Connection closed with server")
            break
        else:
            print("operation ", operation, " not valid")
            print("Type 'help' without quotes to get the list of operations")
    tcpClientA.close() 
