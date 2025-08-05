# actors/storage_actor.py
from thespian.actors import Actor

class StorageActor(Actor):
    def __init__(self, file_path):
        self.file_path = file_path

    def receiveMessage(self, message, sender):
        with open(self.file_path, 'a') as file:
            file.write(f"{message}\n")
        self.send(sender, "Datos almacenados")
