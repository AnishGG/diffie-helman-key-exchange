import os
import sys
import math
import struct
import random
import pickle
from datetime import datetime
from des import DesKey
import settings

class sharedKey:
    """
    Class to store the shared keys between server and client
    """
    def __init__(self, pub_key_other, private_key):
        self.pub_key_other = pub_key_other
        self.private_key = private_key
        self.calculate()

    def calculate(self):
        self.alpha = self.pub_key_other.alpha
        self.q = self.pub_key_other.q
        self.Y = compute_exp_modulo(self.pub_key_other.Y, self.private_key, self.q)

    def __str__(self):
        return "Public key: %s" % self.Y

    def get_key(self):
        ret = str(self.Y)
        if len(ret) >= 8:
            ret = ret[0:8]
        else:
            ret = ret.ljust(8, '0')
        return ret

class PubKey:
    """ 
    Class to store the public keys
    """
    def __init__(self, q = None, alpha = None):
        if q is None:
            self.q = GeneratePrime()                    # Large prime
            self.alpha = GeneratePrimitiveRoot(self.q)  # Primite root
        else:
            self.q = q
            self.alpha = alpha

    def gen_pub_key(self, private_key):
        self.Y = compute_exp_modulo(self.alpha, private_key, self.q)    # Public Key

    def get_pub_key(self):
        return self.Y

    def get_primitive_root(self):
        return self.alpha

    def get_prime(self):
        return self.q

    def __str__(self):
        return "Prime number: %s, Primitive root: %s, Public key: %s" % (self.q,
                self.alpha, self.Y)


class Hdr:
    """
    Header of a general message

    opcode      |       Message
    ============|=============
    10          |       PUBKEY
    20          |       REQSERV
    30          |       ENCMSG
    40          |       REQCOM
    50          |       DISCONNECT
    """
    def __init__(self, opcode, s_addr, d_addr):
        self.opcode = opcode
        self.s_addr = s_addr
        self.d_addr = d_addr

    def get_opcode(self):
        return self.opcode


class Msg:
    """
    A general message storage class
    """
    def __init__(self, hdr, message):
        self.hdr = hdr
        self.allmsg = message

    def get_msg(self):
        return self.allmsg

    def type(self):
        if self.hdr.get_opcode() == settings.PUBKEY:
            return "PUBKEY"
        elif self.hdr.get_opcode() == settings.REQSERV:
            return "REQSERV"
        elif self.hdr.get_opcode() == settings.ENCMSG:
            return "ENCMSG"
        elif self.hdr.get_opcode() == settings.REQCOM:
            return "REQCOM"
        elif self.hdr.get_opcode() == settings.DISCONNECT:
            return "DISCONNECT"

    def make_buff_size(self, final_length):
        add = '~'
        if isinstance(self.allmsg, bytes):
            add = bytes('~', 'utf-8')
        self.allmsg = self.allmsg.ljust(settings.BUFFER_SIZE-final_length, add)
        

"""
Function to compute (a ^ b) mod p
"""
def compute_exp_modulo(a, b, p):
    a, b, p = int(a), int(b), int(p)
    x = 1
    y = a
    while b > 0:
        if(b % 2 == 1):
            x = (x * y) % p
        y = (y * y) % p
        b = int(b/2)
    return x%p


"""
Function to check primality of random generated numbers using Miller-Rabin test
"""
def MillerRabinTest(value, iteration):
    value = int(value)
    if value < 2:
        return 0
    q = value - 1
    k = 0
    while((q&1) == 0):
        q = int(q/2)
        k += 1
    for i in range(0, iteration):
        a = (random.randint(0, settings.MAX_N) % (value - 1)) + 1
        current = q
        flag = 1
        mod_result = compute_exp_modulo(a, current, value)
        for j in range(1, k + 1):
            if mod_result == 1 or (mod_result == value - 1):
                flag = 0
                break
            mod_result = (mod_result * mod_result % value)
        if flag:
            return 0
    return 1

"""
Generate a prime number that is going to be shared globally between client and
server
"""
def GeneratePrime():
    print("Running Miller-Rabin test to find a large prime number...\n")
    random.seed(datetime.now())
    while True:
        current_value = random.randint(1, settings.MAX_N) % settings.MAX_N    # modulo MAX_N is redundant here
        current_value = int(current_value)
        if((current_value&1) == 0):
            current_value += 1
        if(MillerRabinTest(current_value, settings.MAX_ITERATION) == 1):
            return current_value


"""
Generate the primitive root by checking for random numbers
"""
def GeneratePrimitiveRoot(p):
    # Construct sieve of primes
    sieve = [0 for i in range(int(settings.MAX_SIZE)+1)]
    sieve[0] = sieve[1] = 1
    i = 4
    while i < settings.MAX_SIZE:
        sieve[i] = 1
        i += 2
    i = 3
    while i < settings.MAX_SIZE:
        if sieve[i] == 0:
            j = 2 * i
            while j < settings.MAX_SIZE:
                sieve[j] = 1
                j += i
        i += 2
    while True:
        a = random.randint(0, settings.MAX_N) % (p - 2) + 2
        phi = p - 1
        flag = 1
        root = int(math.sqrt(phi))
        for i in range(2, root+1):
            if sieve[i] == 0 and not (phi % i):
                mod_result = compute_exp_modulo(a, phi / i, p)
                if mod_result == 1:
                    flag = 0
                    break
                if MillerRabinTest(phi / i, settings.MAX_ITERATION) and not (phi % int(phi/i)):
                    mod_result = compute_exp_modulo(a, phi / (phi / i), p)
                    if mod_result == 1:
                        flag = 0
                        break
        if flag != 0:
            return a

"""
To encrypt a block of message
"""
def encrypt(msg, shared_keys):
    a, b, c = shared_keys[0].get_key(), shared_keys[1].get_key(), shared_keys[2].get_key()
    key0 = DesKey(bytes(a, 'utf-8'))
    key1 = DesKey(bytes(b, 'utf-8'))
    key2 = DesKey(bytes(c, 'utf-8'))
    ret = key0.encrypt(msg, padding=True)
    ret = key1.decrypt(ret)
    ret = key2.encrypt(ret)
    return ret

def decrypt(msg, shared_keys):
    a, b, c = shared_keys[0].get_key(), shared_keys[1].get_key(), shared_keys[2].get_key()
    key0 = DesKey(bytes(a, 'utf-8'))
    key1 = DesKey(bytes(b, 'utf-8'))
    key2 = DesKey(bytes(c, 'utf-8'))
    ret = key2.decrypt(msg)
    ret = key1.encrypt(ret)
    ret = key0.decrypt(ret, padding=True)
    return ret

"""
Function extends the message when size of the message is less than the buffer
size
"""
def handle_message_size(msg, hdr):
    if len(pickle.dumps(msg)) < settings.BUFFER_SIZE:
        msg.make_buff_size(len(pickle.dumps(Msg(hdr, ""))))

"""
Helper function to send a file over a connection
"""
def send_file(conn, file_name, source_add, dest_add, shared_keys):

    hdr = Hdr(settings.ENCMSG, source_add, dest_add)
    f = open(file_name, 'rb')
    final_text = b""
    l = f.read(settings.BUFFER_SIZE)
    while l:
        final_text += l
        l = f.read(settings.BUFFER_SIZE)
    f.close()

    final_text = encrypt(final_text, shared_keys)
    w = open("data/tmp.txt", 'wb')
    w.write(final_text)
    w.close()
    f1 = open("data/tmp.txt", 'rb')

    msg = Msg(hdr, "")      # Test msg to find empty msg's size
    szz = len(pickle.dumps(msg))

    l = f1.read(settings.BUFFER_SIZE - szz)

    msg = Msg(hdr, l)
    assert(len(pickle.dumps(msg)) <= settings.BUFFER_SIZE)
    while l:
        # Handling when size of the message to be sent is less than buffer size
        handle_message_size(msg, hdr)
        conn.send(pickle.dumps(msg))
        l = f1.read(settings.BUFFER_SIZE - szz)
        msg = Msg(hdr, l)
    f1.close()

    hdr = Hdr(settings.REQCOM, source_add, dest_add)
    msg = Msg(hdr, "File sending done")
    handle_message_size(msg, hdr)
    conn.send(pickle.dumps(msg))
    print("FILE SENDING DONE")

"""
Sends a disconnect request when a file is not present in the server
"""
def file_not_present(conn, source_add, dest_add):
    hdr = Hdr(settings.DISCONNECT, source_add, dest_add)
    final_text = b"File not found at server"
    msg = Msg(hdr, final_text)
    handle_message_size(msg, hdr)
    conn.send(pickle.dumps(msg))
    print("File not present in server")

"""
Helper function to save the file at client side
"""
def recv_file(conn, file_name, shared_keys):
    packet = conn.recv(settings.BUFFER_SIZE)
    packet = pickle.loads(packet)
    if packet.type() == "DISCONNECT":
        return "File not present in server"

    f = open(file_name, 'wb')
    final_text = b""
    while packet.type() == "ENCMSG":
        final_text += packet.get_msg().strip(b'~')
        packet = conn.recv(settings.BUFFER_SIZE)
        packet = pickle.loads(packet)
    data = decrypt(final_text, shared_keys)
    f.write(data)
    f.close()
    return "File recieving done"

"""
Helper function to send messages over a connection
"""
def send_data(conn, MESSAGE):
    msg = struct.pack('>I', len(MESSAGE)) + MESSAGE
    total_sent = 0
    while total_sent < len(msg):
        sent = conn.send(msg[total_sent:total_sent+settings.BUFFER_SIZE])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total_sent += sent


"""
Read message length and unpack it into a integer
"""
def recv_data(conn):
    raw_msglen = recvall(conn, 4)
    if not raw_msglen:
        raise RuntimeError("No data to recieve in the socket; Aborting")
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(conn, msglen)

"""
Helper function to recieve n bytes or return None if EOF is hit
"""
def recvall(conn, n):
    from_client = bytearray()
    while len(from_client) < n:
        size_to_be_recieved = min(n, settings.BUFFER_SIZE)
        packet = conn.recv(size_to_be_recieved)
        if not packet:
            break
        from_client.extend(packet)
    return from_client
