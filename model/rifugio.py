# creo la classe rifugio che rappresenta un nodo del grafo
from dataclasses import dataclass

@dataclass
class Rifugio:
    id: int
    nome: str
    localita: str
    altitudine: int
    capienza: int
    aperto: int

    def __eq__(self, other):
        return isinstance(other, Rifugio) and self.id == other.id

    def __str__(self):
        return f"{self.nome} ({self.localita})"
        # return f"Rifugio (id: {self.id}, nome: {self.localita}, altitudine: {self.altitudine}, capienza: {self.capienza}, aperto: {self.aperto})"
        # sennò nell'output mi da tutto

    # se uso oggetti Rifugio come chiavi di dizionari o come nodi di Networkx mi serve la def hash:
    def __hash__(self):
        return hash(self.id)