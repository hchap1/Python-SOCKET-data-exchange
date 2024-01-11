import socket, threading, pygame

# Initalize pygame
pygame.init()
screen = pygame.display.set_mode((400, 800), vsync=1)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 18)

class message_object:
    def __init__(self, author, timestamp, message_data):
        self.author = author
        self.timestamp = timestamp
        self.message_data = message_data

class client_handler:
    def __init__(self, username, server_ip, server_port, target_chat_log):
        # Ask for a connection from the server
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_ip, server_port))

        # Username, hostname, ip
        self.username = username
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        self.running = True
        self.listening_thread = threading.Thread(target=lambda:self.listen_for_messages(target_chat_log))
        self.listening_thread.start()

    def send_message(self, message):
        # Encode and send the message to the server
        formatted_message = "%s!<|>!%s" % (self.username, message)
        encoded_message = formatted_message.encode()
        print("SENT MESSAGE")
        self.s.send(encoded_message)

    def listen_for_messages(self, target_chat_log):
        while self.running:
            valid = False
            try:
                # Try to receive messages
                message = self.s.recv(1024).decode()
                valid = True
            except ConnectionResetError:
                # Stop receiving messages if server closed
                print("SERVER CLOSED")
                self.running = False
            if valid:
                # If a message was received, decode it and add it to the local chat log
                author, timestamp, message_data = message.split("|")
                message = message_object(author, timestamp, message_data)
                target_chat_log.log.append(message)
                print(message.message_data)

class chat_log:
    def __init__(self):
        self.log = []

# Temporary
server_ip = "192.168.4.123"
server_port = 69
username = input("Username?\n> ")

local_chat_log = chat_log()
client = client_handler(username, server_ip, server_port, local_chat_log)

app_active = True
message_draft = ""
scroll = 0

allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*(),./_+"

while app_active:
    deltatime = clock.tick(60)
    screen.fill((255, 255, 255))

    # Render the chatlog to the screen
    message_y = 0
    for message in local_chat_log.log[::-1]:
        message_y += 20

        y_pos = 650 - message_y + scroll

        if y_pos < 650 and y_pos > -50:
            # Create and render the text
            text = font.render("%s: %s" % (message.author, message.message_data), True, [0, 0, 0], [255, 255, 255])
            # The very bottom pixel witll be x, 800
            screen.blit(text, (20, y_pos))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_active = False

        elif event.type == pygame.KEYDOWN:
            # Get the key symbol
            key = pygame.key.name(event.key)

            if key in allowed_characters:
                message_draft += key

            if key == "space":
                message_draft += " "

            else:
                if key == "backspace": 
                    message_draft = message_draft[:len(message_draft) - 1]
                
                if key == "return":
                    client.send_message(message_draft)
                    message_draft = ""

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                scroll += 10
            elif event.button == 5:  # Scroll down
                scroll -= 10
    
    if message_draft.strip() != "": 
        message_field = font.render(message_draft.strip(), True, [0, 0, 0], [255, 255, 255])
        screen.blit(message_field, [20, 725])

    else:
        message_field = font.render("Enter a message.", True, [0, 0, 0], [255, 255, 255])
        screen.blit(message_field, [20, 725])

    # Update screen
    pygame.display.flip()

# Clean up pygame
pygame.quit()