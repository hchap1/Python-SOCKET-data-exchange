import socket, datetime, threading

class message_object:
    def __init__(self, author:str, timestamp:str, message:str):
        self.author = author
        self.timestamp = timestamp
        self.message = message

class server_object:
    def __init__(self):
        self.clients = {}
        self.chat_log = []

    def disconnect_client(self, username:str):
        self.clients[username].client.close()
        self.clients.pop(username)

    def distribute_message(self, message:message_object):
        print("MESSAGE RECEIVED FROM %s: %s" % (message.author, message.message))
        self.chat_log.append(message)
        for client in self.clients.keys():
            self.clients[client].received_message(message)

class client_object:
    def __init__(self, client, server:server_object, addr:str):
        print("CLIENT CONNECTED")
        self.addr = addr
        self.client = client
        self.server = server
        self.server.clients[addr] = self

    def sent_message(self):
        self.running = True
        while self.running:
            valid = False
            try: 
                # Save all data since last call into a 1024 bit buffer.
                message = self.client.recv(1024).decode()
                valid = True
            except ConnectionResetError: 
                # Client Disconnected
                self.running = False
                print("CLIENT DISCONNECTED: %s" % self.addr)
            if valid:
                # Message exists
                username, message_data = message.split("!<|>!")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = message_object(username, timestamp, message_data)
                # Add to server log for distribution later
                self.server.chat_log.append(message)
                self.server.distribute_message(message)

    def received_message(self, message:message_object):
        # Format relevant data into a string and send to client
        encoded_string = ("%s|%s|%s" % (message.author, message.timestamp, message.message)).encode()
        self.client.send(encoded_string)
                
def initialize(port:int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen()
    return s

def sort_clients(s:socket.socket, server:server_object):
    while True:
        # Listen for clients
        client, addr = s.accept()
        ip = addr[0]

        # Create a client object from this information. Client adds itself to the server dictionary (so that username can be established later)
        instance_of_client = client_object(client, server, ip)
        client_message_listener = threading.Thread(target=instance_of_client.sent_message)
        client_message_listener.start()

# Initialize the server, do not accept clients yet.
s = initialize(69)
server = server_object()

# Start listening for clients
client_connection_thread = threading.Thread(target=lambda:sort_clients(s, server))
client_connection_thread.start()
