import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from thespian.actors import Actor, ActorSystem
import re

# Función para extraer el precio de MercadoLibre
def scrape_mercadolibre(soup):
    # Precio
    price_tag = soup.find('meta', {'itemprop': 'price'})
    price = price_tag['content'] if price_tag else 'No encontrado'
    
    # Disponibilidad (puede variar según el stock del producto)
    available_tag = soup.find('span', {'class': 'ui-pdp-buybox__quantity__available'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    
    # Promoción
    promotion_tag = soup.find('span', {'class': 'ui-pdp-price__second-line__sale-price'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    # Descripción
    description = ''
    description_div = soup.find('div', {'class': 'ui-pdp-description'})
    if description_div:
        description = description_div.get_text(strip=True)

    return price, availability, promotion, description

# Función actualizada para extraer el precio de Tiendamia
def scrape_tiendamia(soup):
    # Precio
    price_tag = soup.find('span', class_='currency_price')
    price = price_tag.text.strip().replace('AR$', '').replace('.', '').replace(',', '.') if price_tag else 'No encontrado'

    # Disponibilidad
    available_tag = soup.find('div', {'class': 'product-information'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    
    # Promoción
    promotion_tag = soup.find('div', {'class': 'badge-sale'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    return price, availability, promotion

def scrape_fullh4rd(soup):
    # Precio
    price_tag = soup.find('div', {'class': 'price-special-container'})
    price = 'No encontrado'
    if price_tag:
        price_text = price_tag.text.strip()
        # Usar expresión regular para extraer solo los números del precio
        price_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', price_text)
        if price_match:
            price = price_match.group(1)

    # Disponibilidad
    available_tag = soup.find('span', {'class': 'availability-status'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'

    # Promoción (por ejemplo, buscando si hay alguna clase o etiqueta de promoción)
    promotion_tag = soup.find('div', {'class': 'promotion-label'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    # Descripción
    description = ''
    info_div = soup.find('div', class_='info air')
    if info_div:
        # Extraer todo el texto de la div, excluyendo los tags HTML
        description = ' '.join(info_div.stripped_strings)

    return price, availability, promotion, description


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
            price, availability, promotion, description = scrape_mercadolibre(soup)
        elif 'tiendamia.com' in domain:
            price, availability, promotion = scrape_tiendamia(soup)
            description = 'N/A'  # Tiendamia no incluye descripción en esta implementación
        elif 'fullh4rd.com' in domain:
            price, availability, promotion, description = scrape_fullh4rd(soup)
        else:
            price, availability, promotion, description = 'Dominio no soportado', 'N/A', 'N/A', 'N/A'

        self.send(sender, (url, price, availability, promotion, description))

# Actor para comparar precios
class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price, avail, promo, desc) for source, price, avail, promo, desc in prices if price != 'No encontrado' and price != 'Dominio no soportado']
        
        if valid_prices:
            # Encontrar el mejor precio
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            result = (
                f"Mejor precio: {best_price[1]} en {best_price[0]}\n"
                f"Disponibilidad: {best_price[2]}\n"
                f"Promoción: {best_price[3]}\n"
                f"Descripción: {best_price[4][:2000]}..."  # Mostramos los primeros 200 caracteres de la descripción
            )
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
    
    # Imprimir el resultado final (incluyendo disponibilidad y promoción)
    print(future)
    
    # Terminar el sistema de actores
    actor_system.shutdown()

if __name__ == "__main__":
    main()

#JOSE EL MEJOR PROFESOR 