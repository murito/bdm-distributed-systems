import datetime
import json
import random
from settings import BOARD_OFFSET_X, BOARD_OFFSET_Y, TILE_SIZE

def json_packet(identifier, sender, players, color, x, y, direction, ip, port, coin_pos = (0,0), outgoing_player = False, defeated=False):
    cx,cy = coin_pos
    return {
        "players": players,
        "id": identifier,
        "from": sender,
        "color": color,
        "x": x,
        "y": y,
        "direction": direction,
        "ip": ip,
        "port": port,
        "is_evil": False,
        "outgoing_player": outgoing_player,
        "coin_initial_position": f"{cx},{cy}",
        "defeated": defeated
    }


def place_random(board):
    empty_cells = [
        (col_idx, row_idx)
        for row_idx, row in enumerate(board)
        for col_idx, cell in enumerate(row)
        if cell == '0'
    ]
    if not empty_cells:
        print("⚠️ No hay celdas vacías para colocar la moneda.")
        return

    col, row = random.choice(empty_cells)
    return (
        BOARD_OFFSET_X + col * TILE_SIZE,
        BOARD_OFFSET_Y + row * TILE_SIZE
    )


def recv_all(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def get_json_by_id(json_array, target_id):
    return [item for item in json_array if item["id"] == target_id]

def get_json_by_field(json_array, target_field, target_value):
    return [item for item in json_array if item[target_field] == target_value][0]

def update_object_by_id(data_list, target_id, new_properties):
    for item in data_list:
        if item.get('id') == target_id:
            item.update(new_properties)
            return True  # Object found and updated
    return False  # Object with target_id not found

def update_object_property_by_id(data_list, target_id, property_to_update, new_value):
    for obj in data_list:
        if obj.get('id') == target_id:  # Assuming 'id' is the key for the identifier
            obj[property_to_update] = new_value
            return True  # Object found and updated
    return False  # Object with target_id not found

def player_exists(list_items, searched_id):
    found = False
    for item in list_items:
        if item.get("id") == searched_id:
            found = True
            break
    return True if found else False

def packet_data(json_arg):
    return json.dumps(json_arg)

def unpack_data(data):
    return json.loads(data.decode())

def get_bit(numbr, i):
    return (numbr >> i) & 1

def get_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S %Z")