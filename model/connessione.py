# creo la classe connessione che rappresenta un arco del grafo (sentiero tra due rifugi)
from dataclasses import dataclass

from model.rifugio import Rifugio


@dataclass
class Connessione:
    id: int
    id_rifugio1: Rifugio
    id_rifugio2: Rifugio
    distanza: int
    difficolta: str
    durata: str
    anno: int

    def __eq__(self, other):
        return isinstance(other, Connessione) and self.id == other.id

    def __str__(self):
        return f"id: {self.id}, Connessione {self.id_rifugio1} - {self.id_rifugio2}, distanza: {self.distanza}, difficolta: {self.difficolta}, durata: {self.durata}, anno: {self.anno}"


