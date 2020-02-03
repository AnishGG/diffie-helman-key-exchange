3DES implementation with Diffie Hellman key exchange
====================================================

Suppose there are n users A (clients) want to securely access the files stored in the database of a user B (server).
At first, each client will make a connection using socket with the server B and then will establish three symmetric keys, say K1 , K2 and K3 which will be used for encryption and decryption using the 3DES with three keys symmetric cryptosystem.

### Dependencies
* python3 is needed in order to run the server and client. It can be installed using the following command.

```bash
apt-get install python3

```
* All the dependencies of the project are given in `requirements.txt`, which can be installed using:

```bash
pip3 install -r requirements.txt

# If you don't have pip3 installed on your system, run:
apt-get install python3-pip
```

To run the server and client, follow the given steps:
```bash
cd server
python3 server.py

# Open a new terminal
cd ../client
python3 client.py 127.0.0.1

# Type 'help' to find out all the commands
```

The protocol messages used in the implementation are provided below

| Opcode |   Message  |                                    Description                                    |
|:------:|:----------:|:---------------------------------------------------------------------------------:|
|   10   |   PUBKEY   |          Public key Ya/Yb sent to the server/client by the client/server          |
|   20   |   REQSERV  | Request for service (transferring a requested file) from the server to the client |
|   30   |   ENCMSG   |      Sending encrypted message(s) for the file from the server to the client      |
|   40   |   REQCOM   |              Request completion message from the server to the client             |
|   50   | DISCONNECT |           Disconnect request message sent from the client to the server           |

### Extra files information
* All the global settings are stored in `settings.py` present in the root directory.
* The common data structures and functions used by server and client side are stored in `common.py` also present in the root directory.
* All the extra dependencies for running the server are stored in `requirements.txt`, which can be installed as described above.
