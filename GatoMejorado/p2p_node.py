"""
Sep 20, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
P2P Node
"""
import datetime
import socket
import threading

# Pool for active connections
peers = []

def get_bit(numbr, i):
    return (numbr >> i) & 1

def get_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S %Z")

# Manage client connections
def handle_client(conn, addr, gato):
    print(f"[+] Connected with: {addr}")

    # go to game screen
    ip, port = addr
    gato.CURRENT_SCREEN = 3 # go to game screen

    # Update connection information
    gato.label_remote_ip.update("Remote IP: " + str(ip))
    gato.label_remote_port.update("Remote Port: " + str(port))

    # Wait a little before processing moves
    gato.clock.tick(30)

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            # decode string
            real_data = int(data.decode())

            # receive winner or draw
            if get_bit(real_data, 12) == 1:
                gato.winner = 1

            if get_bit(real_data, 13) == 1:
                gato.winner = 2

            if get_bit(real_data, 14) == 1:
                gato.winner = 3 # draw

            # set the local player based on network data received
            if gato.player == 0:
                remote_player = get_bit(real_data, 0)
                player = 'O' if( remote_player == 1 ) else 'X'
                gato.player = 2 if( remote_player == 1 ) else 1
                gato.label_player.update("Player: " + player)

            # set the turn
            if gato.player == 1:
                gato.turn = get_bit(real_data, 2) == 0

            if gato.player == 2:
                gato.turn = get_bit(real_data, 2) == 1

            # get player moving
            player_moving = 1 if get_bit(real_data, 1) == 0 else 2

            # Update moves in the current board
            current_bit = 2
            grid_row = 0
            for row in gato.game_state:
                grid_col = 0
                for col in row:
                    current_bit += 1
                    if col == 0 and get_bit(real_data, current_bit) == 1:
                        gato.game_state[grid_row][grid_col] = player_moving
                    grid_col += 1
                grid_row += 1

            # update the bit state
            gato.game_state_bits = real_data

            print(f"[{get_date()} - {addr}]: {data.decode()}")
        except:
            break

    gato.CURRENT_SCREEN = 1
    gato.reset()

    print(f"[-] Disconnected from: {addr}")
    peers.remove(conn)
    conn.close()

# Start main server
def start_server(port, gato):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', int(port)))
    server.listen()

    print(f"[Server] Listening on 127.0.0.1:{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(conn, addr, gato))
        thread.start()

# Client connect to another P2P node
def connect_to_peer(peer_ip, peer_port, gato):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, peer_port))
        peers.append(client)
        print(f"[Client] Connected to {peer_ip}:{peer_port}")

        # board positions are encoded in bits, less significative is the player
        gato.player = 1

        # turn the 1st bit to one, you're player X
        gato.game_state_bits = gato.game_state_bits | 1

        #turn your turn
        gato.turn = True

        # send the new state
        broadcast_message( str(gato.game_state_bits) )

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(client, (peer_ip, peer_port), gato))
        thread.start()
    except Exception as e:
        print(f"[Error] We can't connect to {peer_ip}:{peer_port} - {e}")

# Send message to all the connected nodes
def broadcast_message(message):
    for peer in peers:
        try:
            peer.sendall(message.encode())
        except:
            pass