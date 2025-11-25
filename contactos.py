__author__ = "Nicolas Steven Florez Chicaiza"
__license__ = "GLP"
__version__ = "1.0.0"
__email__ = "nicolas.florezch@campusucc.edu.co"

import csv, os

ARCHIVO = "contactos.csv"

class Contacto:
    def __init__(self, nombre, telefono, correo, cargo):
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.cargo = cargo

class Directorio:
    def __init__(self):
        self.contactos = []
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, newline='', encoding='utf-8') as f:
                for fila in csv.DictReader(f):
                    self.contactos.append(Contacto(**fila))

    def guardar(self):
        with open(ARCHIVO, 'w', newline='', encoding='utf-8') as f:
            campos = ['nombre', 'telefono', 'correo', 'cargo']
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for c in self.contactos:
                writer.writerow(c.__dict__)

    def registrar(self, nombre, telefono, correo, cargo):
        if any(c.correo == correo for c in self.contactos):
            print("❌ Ya existe un contacto con ese correo.")
            return
        self.contactos.append(Contacto(nombre, telefono, correo, cargo))
        self.guardar()
        print("✅ Contacto registrado.")

    def buscar(self, criterio):
        encontrados = [c for c in self.contactos if criterio.lower() in (c.nombre + c.correo).lower()]
        if encontrados:
            for c in encontrados:
                print(f"{c.nombre} | {c.telefono} | {c.correo} | {c.cargo}")
        else:
            print("No se encontró ningún contacto.")

    def listar(self):
        if not self.contactos:
            print("No hay contactos registrados.")
        else:
            print("\n=== LISTA DE CONTACTOS ===")
            for c in self.contactos:
                print(f"{c.nombre} | {c.telefono} | {c.correo} | {c.cargo}")

    def eliminar(self, correo):
        for c in self.contactos:
            if c.correo == correo:
                self.contactos.remove(c)
                self.guardar()
                print("🗑️ Contacto eliminado.")
                return
        print("No existe un contacto con ese correo.")


def menu():
    d = Directorio()
    while True:
        print("""
====== CONNECTME ======
1. Registrar contacto
2. Buscar contacto
3. Listar contactos
4. Eliminar contacto
5. Salir
""")
        op = input("Seleccione una opción: ")
        if op == "1":
            d.registrar(input("Nombre: "), input("Teléfono: "), input("Correo: "), input("Cargo: "))
        elif op == "2":
            d.buscar(input("Nombre o correo: "))
        elif op == "3":
            d.listar()
        elif op == "4":
            d.eliminar(input("Correo del contacto: "))
        elif op == "5":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
