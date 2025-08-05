# actors/search_actors.py
from thespian.actors import Actor
import requests
from bs4 import BeautifulSoup

class SearchActor(Actor):
    def __init__(self, product_name, source_url, parse_function):
        self.product_name = product_name
        self.source_url = source_url
        self.parse_function = parse_function

    def receiveMessage(self, message, sender):
        if message.get('action') == 'fetch_price':
            response = requests.get(self.source_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            result = self.parse_function(soup)
            self.send(sender, {'product': self.product_name, 'source': self.source_url, 'data': result})

# Define parse functions here

def parse_mercadolibre(soup):
    price_tag = soup.find('meta', {'itemprop': 'price'})
    price = price_tag['content'] if price_tag else 'No encontrado'
    available_tag = soup.find('span', {'class': 'ui-pdp-buybox__quantity__available'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    promotion_tag = soup.find('span', {'class': 'ui-pdp-price__second-line__sale-price'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'
    description = soup.find('div', {'class': 'ui-pdp-description'}).get_text(strip=True) if soup.find('div', {'class': 'ui-pdp-description'}) else ''
    return price, availability, promotion, description

def parse_tiendamia(soup):
    price_tag = soup.find('span', {'class': 'precio'})
    price = price_tag.text.strip() if price_tag else 'No encontrado'
    available_tag = soup.find('span', {'class': 'available'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    promotion_tag = soup.find('span', {'class': 'promotion'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'
    description = soup.find('div', {'class': 'description'}).get_text(strip=True) if soup.find('div', {'class': 'description'}) else ''
    return price, availability, promotion, description

def parse_fullh4rd(soup):
    price_tag = soup.find('div', {'class': 'precio'})
    price = price_tag.text.strip() if price_tag else 'No encontrado'
    available_tag = soup.find('span', {'class': 'available'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    promotion_tag = soup.find('span', {'class': 'promotion'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'
    description = soup.find('div', {'class': 'description'}).get_text(strip=True) if soup.find('div', {'class': 'description'}) else ''
    return price, availability, promotion, description
