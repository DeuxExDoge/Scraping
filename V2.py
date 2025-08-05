import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from thespian.actors import Actor, ActorSystem

# Función para extraer el precio de MercadoLibre
def scrape_mercadolibre(soup):
    price_tag = soup.find('meta', {'itemprop': 'price'})
    return price_tag['content'] if price_tag else 'No encontrado'

# Función actualizada para extraer el precio de Tiendamia
def scrape_tiendamia(soup):
    # Buscar el span que contiene el precio en Tiendamia
    price_tag = soup.find('span', class_='currency_price')
    if price_tag:
        # Limpiar el precio y formatearlo
        price = price_tag.text.strip().replace('AR$', '').replace('.', '').replace(',', '.')
        return price
    return 'No encontrado'

# Función para extraer el precio de FullH4rd
def scrape_fullh4rd(soup):
    price_tag = soup.find('div', {'class': 'precio'})
    return price_tag.text.strip() if price_tag else 'No encontrado'

# Actor para hacer scraping de una URL
class ScraperActor(Actor):
    def receiveMessage(self, message, sender):
        url = message
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Identificar el dominio de la URL
        domain = urlparse(url).netloc

        # Lógica de scraping según el dominio
        if 'mercadolibre.com' in domain:
            price = scrape_mercadolibre(soup)
        elif 'tiendamia.com' in domain:
            price = scrape_tiendamia(soup)
        elif 'fullh4rd.com' in domain:
            price = scrape_fullh4rd(soup)
        else:
            price = 'Dominio no soportado'

        self.send(sender, (url, price))

# Actor para comparar precios
class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price) for source, price in prices if price != 'No encontrado' and price != 'Dominio no soportado']
        
        if valid_prices:
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            result = f"Mejor precio: {best_price[1]} en {best_price[0]}"
        else:
            result = "No se encontraron precios válidos."
        
        self.send(sender, result)

def select_product():
    print("Selecciona el producto que deseas comparar:")
    print("1. Mouse")
    print("2. Teclado")
    print("3. Auriculares")
    choice = input("Ingresa el número de tu elección: ")
    
    if choice == '1':
        return urls_Mouses
    elif choice == '2':
        return urls_Teclados
    elif choice == '3':
        return urls_Auriculares
    else:
        print("Opción no válida. Selecciona 1, 2 o 3.")
        return select_product()  # Volver a preguntar si la opción es inválida


# URLs proporcionadas
urls_Mouses = [
    'https://www.mercadolibre.com.ar/logitech-g-series-lightspeed-g502-negro/p/MLA15173180',
    'https://tiendamia.com/ar/producto?amz=B07L4BM851&pName=Logitech%20G502%20Lightspeed%20Wireless%20Gaming%20Mouse%20with%20Hero%2025K%20Sensor&comma;%20PowerPlay%20Compatible&comma;%20Tunable%20Weights%20and%20Lightsync%20RGB%20-%20Black',
    'https://fullh4rd.com.ar/prod/12631/mouse-logitech-g502-wireless-gaming-lightspeed-910-005566',
]

urls_Teclados = [
    'https://www.mercadolibre.com.ar/redragon-kumara-k552-negro-rgb-qwerty-espanol-latinoamerica-outemu-red/p/MLA19472215?product_trigger_id=MLA22657030&quantity=1',
    'https://tiendamia.com/ar/producto?amz=B07D3FJW3S&pName=K552-R%20KUMARA%20Rainbow%20RGB%20Backlit%20Mechanical%20Gaming%20Keyboard',
    'https://fullh4rd.com.ar/prod/9680/teclado-gamer-redragon-kumara-k552-rainbow-red-switch'
]

urls_Auriculares = [
    'https://www.mercadolibre.com.ar/auriculares-gamer-hyperx-cloud-stinger-2-negro-519t1aa/p/MLA23444052#polycard_client=search-nordic&searchVariation=MLA23444052&position=10&search_layout=stack&type=product&tracking_id=52fdbf5d-5d50-4445-87b1-8459441a26df&wid=MLA1435120405&sid=search',
    'https://tiendamia.com/ar/producto?amz=B0B8PGDMWK&pName=Cloud%20Stinger%202%20&ndash;%20Gaming%20Headset&comma;%20DTS%20Headphone&colon;X%20Spatial%20Audio&comma;%20Lightweight%20Over-Ear%20Headset%20with%20mic&comma;%20Swivel-to-Mute%20Function&comma;%2050mm%20Drivers&comma;%20PC%20Compatible&comma;%20Black',
    'https://fullh4rd.com.ar/prod/18028/auriculares-hp-hyperx-cloud-stinger-core-wireless-4p4f0aa'
]

# Función principal para iniciar el sistema de actores
def main():
    urls = select_product()  # Selecciona el producto basado en la opción del usuario
    actor_system = ActorSystem()  # Crear el sistema de actores
    scraper_actors = [actor_system.createActor(ScraperActor) for _ in urls]
    compare_actor = actor_system.createActor(CompareActor)
    
    # Enviar las URLs a los actores scraper
    future = actor_system.ask(compare_actor, [(actor_system.ask(scraper, url, 10)) for scraper, url in zip(scraper_actors, urls)], 10)
    
    # Imprimir el resultado final
    print(future)
    
    # Terminar el sistema de actores
    actor_system.shutdown()

if __name__ == "__main__":
    main()

