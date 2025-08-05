import argparse
import json
import socket
from thespian.actors import ActorSystem
from actors.search_actors import SearchActor, parse_mercadolibre, parse_tiendamia, parse_fullh4rd
from actors.storage_actor import StorageActor
from actors.compare_actor import CompareActor

SERVER_IP = '192.168.0.183'
SERVER_PORT = 65432

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Servidor escuchando en {SERVER_IP}:{SERVER_PORT}")

    storage_actors = {
        'Mouse': StorageActor('data/mouse_price_data.txt'),
        'Teclado': StorageActor('data/teclado_price_data.txt'),
        'Auriculares': StorageActor('data/auriculares_price_data.txt')
    }

    def handle_client_connection(client_socket):
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            try:
                data = json.loads(message)
                product_name = data.get('product', '')
                if product_name in storage_actors:
                    storage_actors[product_name].receiveMessage(data)
                    print(f"Datos recibidos y guardados para {product_name}: {data}")
            except Exception as e:
                print(f"Error al procesar mensaje: {e}")

        client_socket.close()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexión establecida con {addr}")
        handle_client_connection(client_socket)

def run_client():
    def send_to_server(data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            message = json.dumps(data)
            client_socket.sendall(message.encode('utf-8'))
            print(f"Enviado al servidor: {data}")

    with open('config/config.json', 'r') as config_file:
        config = json.load(config_file)

    actor_system = ActorSystem()  # Crear el sistema de actores
    search_actors = []

    for product in config['products']:
        product_name = product['name']
        for source in product['sources']:
            if 'mercadolibre' in source:
                search_actor = actor_system.createActor(SearchActor)  # Crear actor
                search_actors.append((search_actor, product_name, source, parse_mercadolibre))
            elif 'tiendamia' in source:
                search_actor = actor_system.createActor(SearchActor)  # Crear actor
                search_actors.append((search_actor, product_name, source, parse_tiendamia))
            elif 'fullh4rd' in source:
                search_actor = actor_system.createActor(SearchActor)  # Crear actor
                search_actors.append((search_actor, product_name, source, parse_fullh4rd))

    def schedule_search():
        for actor, product_name, source, parse_function in search_actors:
            actor_system.tell(actor, {'action': 'fetch_price', 'product_name': product_name, 'source': source, 'parse_function': parse_function})

    # Run searches and send results
    schedule_search()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modo de ejecución: Servidor o Cliente")
    parser.add_argument('--mode', choices=['server', 'client'], required=True, help="Modo de ejecución: server o client")
    args = parser.parse_args()

    if args.mode == 'server':
        run_server()
    elif args.mode == 'client':
        run_client()
