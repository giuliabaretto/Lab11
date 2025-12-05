import networkx as nx
from database.dao import DAO
from model.rifugio import Rifugio # per la idmap
from collections import deque # per l'algoritmo iterativo


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
        # modo 1 - metodo diretto per contare i vicini : self.G.degree(node.id)
        """
        if node.id in self.G: # controlla se l'id del rifugio è nell'insieme dei nodi del grafo
            # se il nodo esiste -> uso degree() che mi dice il numero di connessioni associate a quell'id
            return self.G.degree(node.id)
        return 0 # se l'if è falso restituisco 0
        """

        # modo 2 - uso la lista dei vicini : self.G.neighbors(node.id)
        return len(list(self.G.neighbors(node.id)))


    def get_num_connected_components(self):
        """
        Restituisce il numero di componenti connesse del grafo.
        :return: numero di componenti connesse
        """
        # modo 1 - uso 'connected_components()' e le conto
        return len(list(nx.connected_components(self.G)))

        # modo 2 - metodo diretto per ottenere il conteggio

        """
        return nx.number_connected_components(self.G)
        
        Dalla libreria di networkx:
        Returns the number of connected components.
        The connected components of an undirected graph partition the graph into disjoint sets of nodes. Each of these sets induces a subgraph of graph G that is connected and not part of any larger connected subgraph.
        A graph is connected (is_connected()) if, for every pair of distinct nodes, there is a path between them. If there is a pair of nodes for which such path does not exist, the graph is not connected (also referred to as “disconnected”).
        A graph consisting of a single node and no edges is connected. Connectivity is undefined for the null graph (graph with no nodes) 
        """


# es 2


    # modo 1 - metodi networkX: `dfs_tree()`, `bfs_tree()`
    def get_reachable_bfs_tree(self, start):
        # bfs_tree() esegue una ricerca in ampiezza (Breath-first-search) -> garantisce che i nodi siano visitati in ordine di distanza crescente dal nodo di partenza
        if start not in self.G:
            return []
        # trovo gli id raggiungibili con bfs_tree
        # .nodes mi restituisce tutti gli id (sono i nodi dell'albero bfs)
        reachable_id = list(nx.bfs_tree(self.G, source = start).nodes)
        # escludo il nodo di partenza
        if start in reachable_id:
            reachable_id.remove(start)
        # converto gli id trovati nella lista, in oggetti Rifugio
        return [self._rifugi_dict[id] for id in reachable_id]

    # modo 2 - algoritmo ricorsivo dfs

    # funzione ricorsiva per la dfs
    def _dfs_recursive(self, current_id, visited, reachable_id):
        for neighbor_id in self.G.neighbors(current_id):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                reachable_id.append(neighbor_id)
                self._dfs_recursive(neighbor_id, visited, reachable_id)

    def get_reachable_recursive(self, start):
        # sfrutta la ricorsione
        # richiamo continuamente _dfs_recursive, che va su un vicino non visitato e esplora un singolo sentiero fino alla fine, poi torna indietro e esplora altre diramazioni
        if start not in self.G:
            return []
        # creo set visited e ci aggiungo l'id del nodo di partenza
        visited = set() # il set traccia i nodi gia incontrati
        visited.add(start) # così non lo visito e lo escludo già (come richiesto non devo metterlo nell'elenco da restituire)
        reachable_id = []
        self._dfs_recursive(start, visited, reachable_id) # chiamo la funzione ricorsione
        return [self._rifugi_dict[id] for id in reachable_id]

    # modo 3 - algoritmo iterativo
    def get_reachable_iterative(self, start):
        # simula la bfs senza usare la funzione networkX, usando "deque" (gestisce l'ordine di visita, affinchè la ricerca si espanda in ampiezza) e "set" (registra i nodi trovati)
        # uso un ciclo while al posto della ricorsione
        if start not in self.G:
            return []
        visited = set()
        visited.add(start)
        coda = deque([start]) # creo una coda con il nodo di partenza -> garantisce che i nodi vengano esplorati in ordine di arrivo per livello
        reachable_id = []
        while coda: #ciclo continua finchè ho nodi da esplorare
            nodo = coda.popleft() #estraggo primo elemento a sinistra della coda: nodo che sto processando ora
            # esploro i vicini
            for neighbor_id in self.G.neighbors(nodo):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    coda.append(neighbor_id)
                    reachable_id.append(neighbor_id)
        return [self._rifugi_dict[id] for id in reachable_id]



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
        # eseguo tutti e 3 i metodi che ho creato per trovare l'elenco di rifugi raggiungibili da "start" (componente connessa associata al nodo (rifugio) scelto)

        # prendo l'id, che è l'input per gli algoritmi del grafo
        start = start.id

        # provo le tre tecniche
        # modo 1 - metodi networkX: `dfs_tree()`, `bfs_tree()`
        risultato_bfs_tree = self.get_reachable_bfs_tree(start)

        #modo 2 - algoritmo ricorsivo dfs
        risultato_recursive = self.get_reachable_recursive(start)

        #modo 3 - algoritmo iterativo
        risultato_iterativo = self.get_reachable_iterative(start)

        #debug per confronto (controllo che mi restituiscano la stessa lista di nodi)
        # converto le liste in set (così ignoro ordine di visita e confronto solo contenuto)
        set_bfs_tree = set(risultato_bfs_tree)
        set_recursive = set(risultato_recursive)
        set_iterative = set(risultato_iterativo)

        if set_bfs_tree != set_recursive:
            print("I set di nodi con tecnica bfs_tree e ricorsione non coincidono")
        if set_iterative != set_bfs_tree:
            print("I set di nodi con tecnica iterativa e bfs_tree non coincidono")
        if set_recursive != set_iterative:
            print("I set di nodi con ricorsione e tecnica iterativa non coincidono")

        # restituisco risultato (con una delle tre tecniche a caso)
        return risultato_bfs_tree

