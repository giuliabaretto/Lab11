import networkx as nx
from database.dao import DAO
from model.rifugio import Rifugio # per la idmap


class Model:
    def __init__(self):
        self.G = nx.Graph()
        self._rifugi_list = []
        # creo un dizionario di rifugi
        self._rifugi_dict = {} #idmap {id_rifugio : oggetto_Rifugio}
        self._getRifugi()

    def _getRifugi(self):
        # per caricare tutti i rifugi disponibile nel dizionario id
        self._rifugi_list = DAO.read_rifugio() #lista di oggetti
        if self._rifugi_list:
            self._rifugi_dict = {rifugio.id: rifugio for rifugio in self._rifugi_list}


    def build_graph(self, year: int):
        """
        Costruisce il grafo (self.G) dei rifugi considerando solo le connessioni
        con campo `anno` <= year passato come argomento.
        Quindi il grafo avrà solo i nodi che appartengono almeno ad una connessione, non tutti quelli disponibili.
        :param year: anno limite fino al quale selezionare le connessioni da includere.
        """
        # pulisco il grafo per costruire il nuovo
        self.G.clear()

        # ARCHI -> carico e filtro le connessioni
        connessioni = DAO.read_connessioni_per_anno(self._rifugi_dict, year)

        #se non ci sono connessioni il grafo ha nodi ma nessun arco:
        if not connessioni:
            return

        # lista degli archi - coppie di id
        edges = []
        nodi_coinvolti = set() #id preso una sola volta anche se rifugio fa parte di tanti sentieri
        # rimuovo eventuali nodi isolati (i nodi devono appartenere ad almeno una connessione!)
        for connessione in connessioni:
            #nodi all'estremità dell'arco
            id_1 = connessione.id_rifugio1.id  #dall'oggetto Rifugio all'inizio del sentiero, estraggo id
            id_2 = connessione.id_rifugio2.id

            #questi sono quindi nodi che hanno un sentiero, e li aggiungo ai nodi coinvolti
            nodi_coinvolti.add(id_1)
            nodi_coinvolti.add(id_2)

            # aggiungo la coppia di id (tupla) (=sentiero) alla lista degli archi
            edges.append((id_1, id_2))

        # i rifugi non menzionati nella lista edges hanno grado 0 : sono isolati!
        # aggiungo gli archi, stabilisco le connessioni
        self.G.add_edges_from(edges)
        # -> aggiungo solo i nodi che sono stati effettivamente coinvolti
        self.G.add_nodes_from(nodi_coinvolti)



    def get_nodes(self):
        """
        Restituisce la lista dei rifugi presenti nel grafo.
        :return: lista dei rifugi presenti nel grafo.
        """
        rifugi = []
        for rifugio_id in self.G.nodes:
            rifugi.append(self._rifugi_dict[rifugio_id])
        return rifugi

    def get_num_neighbors(self, node):
        """
        Restituisce il grado (numero di vicini diretti) del nodo rifugio.
        :param node: un rifugio (cioè un nodo del grafo)
        :return: numero di vicini diretti del nodo indicato
        """
        if node.id in self.G: # controlla se l'id del rifugio è nell'insieme dei nodi del grafo
            # se il nodo esiste -> uso degree() che mi dice il numero di connessioni associate a quell'id
            return self.G.degree(node.id)
        return 0 # se l'if è falso restituisco 0


    def get_num_connected_components(self):
        """
        Restituisce il numero di componenti connesse del grafo.
        :return: numero di componenti connesse
        """
        return nx.number_connected_components(self.G)

        """ Dalla libreria di networkx:
        Returns the number of connected components.
        The connected components of an undirected graph partition the graph into disjoint sets of nodes. Each of these sets induces a subgraph of graph G that is connected and not part of any larger connected subgraph.
        A graph is connected (is_connected()) if, for every pair of distinct nodes, there is a path between them. If there is a pair of nodes for which such path does not exist, the graph is not connected (also referred to as “disconnected”).
        A graph consisting of a single node and no edges is connected. Connectivity is undefined for the null graph (graph with no nodes) """

# 2


    def get_reachable(self, start):
        """
        Deve eseguire almeno 2 delle 3 tecniche indicate nella traccia:
        * Metodi NetworkX: `dfs_tree()`, `bfs_tree()`
        * Algoritmo ricorsivo DFS
        * Algoritmo iterativo
        per ottenere l'elenco di rifugi raggiungibili da `start` e deve restituire uno degli elenchi calcolati.
        :param start: nodo di partenza, da non considerare nell'elenco da restituire.

        ESEMPIO
        a = self.get_reachable_bfs_tree(start)
        b = self.get_reachable_iterative(start)
        b = self.get_reachable_recursive(start)

        return a
        """

        # TODO
