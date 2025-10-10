"""
Sep 20, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
P2P Node
"""
import socket
import struct
import threading
import time
import uuid

from settings import pacman_colors
from p2p_helpers import *

# Pool for active connections
peers = []
peer_players = []

# Manage client connections
def handle_client(conn, addr, pacman):
    print(f"[+] Connected with: {addr}")

    ip, port = addr

    # manage players in
    if pacman.whoami == "server":
        # Add new client to the count
        pacman.players_joined += 1

        # assign id and color to client
        random_uuid = uuid.uuid4()
        r, g, b = pacman_colors[pacman.players_joined - 2]
        new_client = json_packet(
            identifier=str(random_uuid),
            sender='server',
            players=pacman.players_joined,
            color=f"{r},{g},{b}", x=0, y=0,
            direction="LEFT",
            ip=ip,
            port=port,
            coin_pos=pacman.coin_initial_position,
            outgoing_player=False,
            defeated=False
        )
        peer_players.append(new_client)

        # Negotiate with the client, id and color
        pkt = packet_data(new_client)
        broadcast_message(pkt, conn)

        # inform the existence of others players to the new client
        for player in peer_players:
            if player['id'] != new_client['id']:
                time.sleep(0.5)
                cx, cy = pacman.coin_initial_position
                update_object_by_id(peer_players, player['id'], {
                    "players": pacman.players_joined,
                    "coin_initial_position": f"{cx},{cy}"
                })
                pkt = packet_data(player)
                broadcast_message(pkt, conn)

    #
    #  Reception of packets start here
    #
    while True:
        try:
            data = recv_all(conn, 4)

            if not data:
                break

            msg_len = struct.unpack("!I", data)[0]
            msg_data = recv_all(conn, msg_len)

            # decode string
            json_data = unpack_data(msg_data)

            # It means you are the server, broadcast the message then
            if pacman.whoami == "server":
                broadcast_message(packet_data(json_data))

            # Messages send by server
            if json_data['from'] == "server":
                if json_data.get('coin_position') is not None:
                    print(json_data)
                    position = json_data.get('coin_position').split(",")
                    pacman.coin_initial_position = (int(position[0]), int(position[1]))

                # Filter the guy that left the game
                if bool(json_data['outgoing_player']):
                    pacman.players_joined -= 1
                    new_data = [item for item in peer_players if item.get("id") != json_data['id']]
                    peer_players[:] = new_data

                # Initial negotiation packet
                if pacman.whoami is None:
                    pacman.players_joined = json_data['players']
                    pacman.whoami = json_data['id']
                    pacman.my_color = json_data['color']

                    # Coin has changed its place
                    position = json_data['coin_initial_position'].split(",")
                    pacman.coin_initial_position = (int(position[0]), int(position[1]))

            # Logic for both, server and client
            if player_exists(peer_players, json_data['id']):
                # Remote controls are caught here
                update_object_by_id(peer_players, json_data['id'], json_data)
            elif not bool(json_data['outgoing_player']):
                print("Incoming player")
                pacman.players_joined = json_data['players']
                peer_players.append(json_data)

        except Exception as e:
            print(f"===> {e}")
            break

    if pacman.players_joined > 1 and pacman.whoami == "server":
        # Remove a player from the list
        pacman.players_joined -= 1

        # get outgoing player
        outgoing_player = get_json_by_field(peer_players, 'port', port)

        # inform the gang this guy left the game
        out_player = json_packet(
            outgoing_player['id'],
            'server',
            pacman.players_joined,
            outgoing_player['color'],
            outgoing_player['x'],
            outgoing_player['y'],
            outgoing_player['direction'],
            outgoing_player['ip'],
            outgoing_player['port'],
            pacman.coin_initial_position,
            True
        )
        pkt = packet_data(out_player)
        broadcast_message(pkt, conn)

        # Filter outgoing player from peer_players
        new_data = [item for item in peer_players if item.get("port") != outgoing_player['port']]
        peer_players[:] = new_data

    peers.remove(conn)
    conn.close()

    print(f"[-] Disconnected from: {addr}")

# Start main server
def start_server(port, pacman):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', int(port)))
    server.listen()

    # identify yourself here
    pacman.whoami = "server"
    pacman.my_color = (255, 255, 0)
    r, g, b = pacman.my_color
    myself = json_packet(
        'server',
        'server',
        pacman.players_joined,
        f"{r},{g},{b}", 0, 0, "LEFT",
        '127.0.0.1',
        8080,
        pacman.coin_initial_position
    )
    peer_players.append(myself)

    print(f"[Server] Listening on 127.0.0.1:{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(conn, addr, pacman))
        thread.start()

# Client connect to another P2P node
def connect_to_peer(peer_ip, peer_port, pacman):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((peer_ip, peer_port))
        peers.append(client)

        print(f"[Client] Connected to {peer_ip}:{peer_port}")

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(client, (peer_ip, peer_port), pacman))
        thread.start()
    except Exception as e:
        print(f"[Error] We can't connect to {peer_ip}:{peer_port} - {e}")

# Send message to all the connected nodes
def broadcast_message(message, source=None):
    m = message.encode()
    length = struct.pack("!I", len(m))
    for peer in peers:
        try:
            if source and peer != source:
                peer.sendall(length + m)
            else:
                peer.sendall(length + m)
        except Exception as e:
            print(f"[Broadcast Error] {e}")
