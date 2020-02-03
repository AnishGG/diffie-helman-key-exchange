# Python TCP Client A
import socket
import pickle
import random
import sys
sys.path.append("../")
from common import send_file, recv_file, sharedKey, PubKey, send_data, recv_data, Hdr, Msg

if __name__ == "__main__":
    host = socket.gethostname() 
    port = 2004
     
    tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    tcpClientA.connect((host, port))
    print(tcpClientA.getsockname())

    # Create 3 public keys to be shared with the server
    a, b, c = PubKey(), PubKey(), PubKey()
    private_a = random.randint(1, a.q - 1)  # Random number between 1 and a.q - 1
    private_b = random.randint(1, b.q - 1)  # Random number between 1 and b.q - 1
    private_c = random.randint(1, c.q - 1)  # Random number between 1 and c.q - 1
    a.gen_pub_key(private_a)
    b.gen_pub_key(private_b)
    c.gen_pub_key(private_c)

    # Create header for public key sharing
    hdr = Hdr(10, tcpClientA.getsockname(), port)
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

    print("Sharing of key over")

    # Send a REQSERV msg
    hdr = Hdr(20, tcpClientA.getsockname(), port)
    msg = Msg(hdr, "input.txt")
    send_data(tcpClientA, pickle.dumps(msg))

    print(recv_file(tcpClientA, "input.txt"))
    tcpClientA.close() 
