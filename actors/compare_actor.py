# actors/compare_actor.py
from thespian.actors import Actor

class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price, avail, promo, desc) for source, price, avail, promo, desc in prices if price != 'No encontrado' and price != 'Dominio no soportado']
        
        if valid_prices:
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
