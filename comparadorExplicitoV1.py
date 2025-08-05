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

# URLs proporcionadas
urls1 = [
    'https://www.mercadolibre.com.ar/logitech-g-series-lightspeed-g502-negro/p/MLA15173180',
    'https://tiendamia.com/ar/producto?amz=B07L4BM851&pName=Logitech%20G502%20Lightspeed%20Wireless%20Gaming%20Mouse%20with%20Hero%2025K%20Sensor&comma;%20PowerPlay%20Compatible&comma;%20Tunable%20Weights%20and%20Lightsync%20RGB%20-%20Black',
    'https://fullh4rd.com.ar/prod/12631/mouse-logitech-g502-wireless-gaming-lightspeed-910-005566',
]

# Función principal para iniciar el sistema de actores
def main():
    actor_system = ActorSystem()  # Crear el sistema de actores
    scraper_actors = [actor_system.createActor(ScraperActor) for _ in urls1]
    compare_actor = actor_system.createActor(CompareActor)
    
    # Enviar las URLs a los actores scraper
    future = actor_system.ask(compare_actor, [(actor_system.ask(scraper, url, 10)) for scraper, url in zip(scraper_actors, urls1)], 10)
    
    # Imprimir el resultado final
    print(future)
    
    # Terminar el sistema de actores
    actor_system.shutdown()

if __name__ == "__main__":
    main()
