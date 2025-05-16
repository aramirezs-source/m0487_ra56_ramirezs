import sqlite3
import os
import re

# --- Configuració base de dades ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "biblioteca.db")

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuaris (
        dni TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        cognoms TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS llibres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titol TEXT NOT NULL,
        autor TEXT NOT NULL,
        dni_prestec TEXT DEFAULT '0'
    )
""")

conn.commit()

# --- Validació DNI ---
def validar_dni(dni):
    patron = r'^\d{8}[A-HJ-NP-TV-Z]$'
    return re.match(patron, dni)

# --- Classe Usuari ---
    """
    Classe que representa un usuari de la biblioteca.

    Atributs:
        nom (str): Nom de l'usuari.
        cognoms (str): Cognoms de l'usuari.
        dni (str): DNI de l'usuari (clau primària).

    Mètodes:
        guardar(): Insereix l'usuari a la base de dades.
        eliminar(): Elimina l'usuari de la base de dades pel seu DNI.
        imprimir_dades(): Mostra les dades de l'usuari.
        introduir_dades(): Demana les dades de l'usuari per consola.
    """
class Usuari:
    def __init__(self, nom="None", cognoms="None", dni="None"):
        self.nom = nom
        self.cognoms = cognoms
        self.dni = dni    

    def guardar(self):
        if not validar_dni(self.dni):
            print("Error: El DNI no és vàlid.")
            return
        try:
            cursor.execute("INSERT INTO usuaris (dni, nom, cognoms) VALUES (?, ?, ?)", (self.dni, self.nom, self.cognoms))
            conn.commit()
            print("Usuari afegit correctament.")
        except sqlite3.IntegrityError:
            print("Error: Ja existeix un usuari amb aquest DNI.")

    def eliminar(self):
        cursor.execute("DELETE FROM usuaris WHERE dni = ?", (self.dni,))
        conn.commit()
        print("Usuari eliminat correctament.")

    def actualitzar(self):
        nou_nom = input("Nou nom (enter per deixar igual): ").strip() or self.nom
        nous_cognoms = input("Nous cognoms (enter per deixar igual): ").strip() or self.cognoms

        cursor.execute("UPDATE usuaris SET nom = ?, cognoms = ? WHERE dni = ?", (nou_nom, nous_cognoms, self.dni))
        conn.commit()
        print("Usuari actualitzat correctament.")

    def imprimir_dades(self):
        print(f"{self.nom} {self.cognoms} : {self.dni}")

    def introduir_dades(self):
        while True:
            self.nom = input("Introdueix el nom: ").strip()
            self.cognoms = input("Introdueix els cognoms: ").strip()
            self.dni = input("Introdueix el DNI: ").strip()
            if not self.nom or not self.cognoms or not self.dni:
                print("Error: Cap camp pot estar buit!")
            elif not validar_dni(self.dni):
                print("Error: DNI no vàlid (ex: 12345678A)")
            else:
                break

# --- Classe Llibre ---
class Llibre:
    """
    Classe que representa un llibre de la biblioteca.

    Atributs:
        titol (str): Títol del llibre.
        autor (str): Autor del llibre.
        dni_prestec (str): DNI de l'usuari que té el llibre (o '0' si està disponible).

    Mètodes:
        guardar(): Insereix el llibre a la base de dades.
        eliminar(id): Elimina el llibre pel seu ID.
        prestar(id, dni): Assigna el llibre a un usuari (si està disponible).
        tornar(id): Torna el llibre (posa dni_prestec a '0').
        imprimir_dades(): Mostra les dades del llibre.
    """

    def __init__(self, titol, autor, dni_prestec='0'):
        self.titol = titol
        self.autor = autor
        self.dni_prestec = dni_prestec

    def guardar(self):
        cursor.execute("INSERT INTO llibres (titol, autor, dni_prestec) VALUES (?, ?, ?)", (self.titol, self.autor, self.dni_prestec))
        conn.commit()
        print("Llibre afegit correctament.")

    @staticmethod
    def eliminar(id):
        cursor.execute("DELETE FROM llibres WHERE id = ?", (id,))
        conn.commit()
        print("Llibre eliminat correctament.")

    @staticmethod
    def actualitzar(id):
        cursor.execute("SELECT titol, autor FROM llibres WHERE id = ?", (id,))
        resultat = cursor.fetchone()
        if resultat:
            titol_actual, autor_actual = resultat
            nou_titol = input(f"Nou títol (enter per deixar '{titol_actual}'): ").strip() or titol_actual
            nou_autor = input(f"Nou autor (enter per deixar '{autor_actual}'): ").strip() or autor_actual

            cursor.execute("UPDATE llibres SET titol = ?, autor = ? WHERE id = ?", (nou_titol, nou_autor, id))
            conn.commit()
            print("Llibre actualitzat correctament.")
        else:
            print("Llibre no trobat.")

    @staticmethod
    def prestar(id, dni):
        cursor.execute("SELECT dni_prestec FROM llibres WHERE id = ?", (id,))
        resultat = cursor.fetchone()
        if resultat:
            if resultat[0] != '0':
                print("Aquest llibre ja està prestat.")
            else:
                cursor.execute("SELECT COUNT(*) FROM llibres WHERE dni_prestec = ?", (dni,))
                comptador = cursor.fetchone()[0]
                if comptador >= 3:
                    print("Aquest usuari ja té 3 llibres prestats.")
                else:
                    cursor.execute("UPDATE llibres SET dni_prestec = ? WHERE id = ?", (dni, id))
                    conn.commit()
                    print("Llibre prestat correctament.")
        else:
            print("Llibre no trobat.")

    @staticmethod
    def tornar(id):
        cursor.execute("SELECT dni_prestec FROM llibres WHERE id = ?", (id,))
        resultat = cursor.fetchone()
        if resultat:
            if resultat[0] == '0':
                print("Aquest llibre no està en préstec.")
            else:
                cursor.execute("UPDATE llibres SET dni_prestec = '0' WHERE id = ?", (id,))
                conn.commit()
                print("Llibre retornat correctament.")
        else:
            print("Llibre no trobat.")

    def imprimir_dades(self):
        estat = f"PRESTAT a {self.dni_prestec}" if self.dni_prestec != '0' else "Disponible"
        print(f"Títol: {self.titol}, Autor: {self.autor}, Estat: {estat}")

# --- Funcions de llistar ---
def llistar_usuaris():
    cursor.execute("SELECT * FROM usuaris")
    usuaris = cursor.fetchall()
    print("\n--- Usuaris ---")
    for u in usuaris:
        print(f"{u[1]} {u[2]} : {u[0]}")
    if not usuaris:
        print("No hi ha usuaris.")

def llistar_llibres():
    cursor.execute("SELECT * FROM llibres")
    llibres = cursor.fetchall()
    print("\n--- Llibres ---")
    for l in llibres:
        estat = f"PRESTAT a {l[3]}" if l[3] != '0' else "Disponible"
        print(f"ID: {l[0]}, Títol: {l[1]}, Autor: {l[2]}, Estat: {estat}")
    if not llibres:
        print("No hi ha llibres.")

# --- Menú principal ---
def menu():
    while True:
        print("\n--- Menú Biblioteca ---")
        print("1. Afegir usuari")
        print("2. Llistar usuaris")
        print("3. Eliminar usuari")
        print("4. Afegir llibre")
        print("5. Llistar llibres")
        print("6. Eliminar llibre")
        print("7. Prestar llibre")
        print("8. Tornar llibre")
        print("9. Actualitzar usuari")
        print("10. Actualitzar llibre")
        print("11. Sortir")

        opcio = input("Selecciona una opció: ")

        if opcio == '1':
            u = Usuari()
            u.introduir_dades()
            u.guardar()
        elif opcio == '2':
            llistar_usuaris()
        elif opcio == '3':
            dni = input("Introdueix el DNI de l'usuari a eliminar: ")
            u = Usuari(dni=dni)
            u.eliminar()
        elif opcio == '4':
            titol = input("Introdueix el títol del llibre: ").strip()
            autor = input("Introdueix l'autor del llibre: ").strip()
            l = Llibre(titol, autor)
            l.guardar()
        elif opcio == '5':
            llistar_llibres()
        elif opcio == '6':
            id = input("Introdueix l'ID del llibre a eliminar: ")
            Llibre.eliminar(id)
        elif opcio == '7':
            id = input("Introdueix l'ID del llibre a prestar: ")
            dni = input("Introdueix el DNI de l'usuari: ")
            if validar_dni(dni):
                Llibre.prestar(id, dni)
            else:
                print("DNI no vàlid.")
        elif opcio == '8':
            id = input("Introdueix l'ID del llibre a tornar: ")
            Llibre.tornar(id)
        elif opcio == '9':
            dni = input("Introdueix el DNI de l'usuari a actualitzar: ")
            cursor.execute("SELECT * FROM usuaris WHERE dni = ?", (dni,))
            usuari = cursor.fetchone()
            if usuari:
                u = Usuari(usuari[1], usuari[2], dni)
                u.actualitzar()
            else:
                print("Usuari no trobat.")
        elif opcio == '10':
            id = input("Introdueix l'ID del llibre a actualitzar: ")
            Llibre.actualitzar(id)
        elif opcio == '11':
            print("Sortint...")
            break
        else:
            print("Opció no vàlida!")

# --- Execució ---
if __name__ == "__main__":
    menu()
    conn.close()
