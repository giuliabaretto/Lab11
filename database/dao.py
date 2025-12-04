from database.DB_connect import DBConnect
from model.rifugio import Rifugio
from model.connessione import Connessione

class DAO:
    """
        Implementare tutte le funzioni necessarie a interrogare il database.
        """
    def __init__(self):
        pass


    # funzione che mi restituisce i sentieri (connessioni) che soddisfano il criterio dell'anno come lista
    # riceve rifugi_dict (dizionario che mappa gli id dei rifugi ai loro oggetti corrispondenti) per convertire gli ID nei rispettivi oggetti Rifugio; e year (anno limite per filtraggio)

    @staticmethod
    def read_connessioni_per_anno(rifugi_dict: dict, year: int):
        connection = DBConnect.get_connection()
        result = []

        if connection is None:
            print("Errore di connessione")
            return None

        # "Creare un grafo non orientato e non pesato che rappresenti la rete escursionistica fino all’anno indicato"
        query = (""" SELECT *
                     FROM connessione
                     WHERE anno <= %s """)

        cursor = connection.cursor(dictionary=True)
        try:
            #cursor.execute(query)
            #result = cursor.fetchall()
            cursor.execute(query, (year,))

            for row in cursor:
                # passo gli oggetti rifugio alla connessione (gli id)
                # li recupero completi
                rifugio1 = rifugi_dict.get(row["id_rifugio1"])
                rifugio2 = rifugi_dict.get(row["id_rifugio2"])
                # creo l'oggetto connessione, dove metto gli oggetti Rifugio al posto degli id numerici
                result.append(Connessione(id=row["id"], id_rifugio1=rifugio1, id_rifugio2=rifugio2, distanza=row["distanza"], difficolta=row["difficolta"], durata=row["durata"], anno=row["anno"]))

        except Exception as e:
            print(f"Errore durante la query: {e}")
            result = None
        cursor.close()
        connection.close()
        return result







    # funzione che mi restituisce tutti i rifugi come lista di oggetti Rifugio
    # risolvo come svolto in aula 1/12

    @staticmethod
    def read_rifugio():
        connection = DBConnect.get_connection()
        result = []

        if connection is None:
            print("Errore di connessione")
            return None

        query = (""" SELECT *
                     FROM rifugio""")

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            for row in cursor: # dove row è un dizionario
                #creo oggetto rifugio dalla classe Rifugio, usando l'unpacking del dizionario
                result.append(Rifugio(**row))

        except Exception as e:
            print(f"Errore durante la query: {e}")
            result = None
        cursor.close()
        connection.close()
        return result



