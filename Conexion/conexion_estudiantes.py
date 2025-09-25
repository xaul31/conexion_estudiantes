import pyodbc
from dotenv import load_dotenv
import os

class ConexionBD:
    def __init__(self):
        load_dotenv()
        self.servidor = os.getenv("DB_SERVER")
        self.base_datos = os.getenv("DB_NAME")
        self.usuario = os.getenv("DB_USER")
        self.contrasena = os.getenv("DB_PASSWORD")
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.servidor};'
                f'DATABASE={self.base_datos};'
                f'UID={self.usuario};'
                f'PWD={self.contrasena}'
            )
            print("Conexión exitosa a SQL Server.")
        except Exception as e:
            print("Error al conectar a la base de datos:", e)

    def cerrar_conexion(self):
        if self.conexion:
            self.conexion.close()
            print("Conexión cerrada.")

    def ejecutar_consulta(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            return cursor.fetchall()
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            return []

    def ejecutar_instruccion(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            self.conexion.commit()
            print("Instrucción ejecutada correctamente.")
        except Exception as e:
            print("Error al ejecutar la instrucción:", e)
            self.conexion.rollback()

def mostrar_menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Listar estudiantes")
    print("2. Agregar estudiante")
    print("3. Buscar estudiante")
    print("4. Eliminar estudiante por ID")
    print("5. Actualizar edad de un estudiante")
    print("6. Mostrar estudiantes con edad ≥ 18")
    print("7. Salir")

def main():
    db = ConexionBD()
    db.conectar()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes")
            print("\n--- Lista de Estudiantes ---")
            for est in estudiantes:
                print(f"ID: {est[0]}, Nombre: {est[1]}, Edad: {est[2]}")
        elif opcion == "2":
            nombre = input("Nombre del estudiante: ").strip()
            if not nombre or len(nombre) < 3:
                print("El nombre debe tener más de 3 caracteres.")
                continue

            try:
                edad = int(input("Edad del estudiante: "))
                if edad < 15 or edad > 100:
                    print("La edad debe estar entre 15 y 100 años.")
                    continue
            except ValueError:
                print("Por favor, ingrese una edad válida.")
                continue

            db.ejecutar_instruccion(
                "INSERT INTO estudiantes (nombre, edad) VALUES (?, ?)", (nombre, edad)
            )
        elif opcion == "3":
            nombre_buscar = input("Ingrese el nombre del estudiante a buscar: ").strip()
            if not nombre_buscar:
                print("El nombre no puede estar vacío.")
                continue

            estudiantes = db.ejecutar_consulta(
                "SELECT * FROM estudiantes WHERE nombre LIKE ?", (f"%{nombre_buscar}%",)
            )
            if estudiantes:
                print("\n--- Resultados de la búsqueda ---")
                for est in estudiantes:
                    print(f"ID: {est[0]}, Nombre: {est[1]}, Edad: {est[2]}")
            else:
                print("No se encontraron estudiantes con ese nombre.")

        elif opcion == "4":
            try:
                id_estudiante = int(input("Ingrese el ID del estudiante a eliminar: "))
                confirmacion = input(f"¿Está seguro de que desea eliminar al estudiante con ID {id_estudiante}? (s/n): ").strip().lower()
                if confirmacion == "s":
                    db.ejecutar_instruccion(
                        "DELETE FROM estudiantes WHERE id = ?", (id_estudiante,)
                    )
                    print(f"Estudiante con ID {id_estudiante} eliminado exitosamente.")
                else:
                    print("Operación cancelada.")
            except ValueError:
                print("Por favor, ingrese un ID válido.")

        elif opcion == "5":
            try:
                id_estudiante = int(input("Ingrese el ID del estudiante cuya edad desea actualizar: "))
                nueva_edad = int(input("Ingrese la nueva edad del estudiante: "))
                if nueva_edad < 15 or nueva_edad > 100:
                    print("La edad debe estar entre 15 y 100 años.")
                    continue

                db.ejecutar_instruccion(
                    "UPDATE estudiantes SET edad = ? WHERE id = ?", (nueva_edad, id_estudiante)
                )
                print(f"Edad del estudiante con ID {id_estudiante} actualizada exitosamente.")
            except ValueError:
                print("Por favor, ingrese valores válidos.")        

        elif opcion == "6":
            estudiantes = db.ejecutar_consulta("SELECT * FROM estudiantes WHERE edad >= 18")
            print("\n--- Estudiantes con edad ≥ 18 ---")
            if estudiantes:
                for est in estudiantes:
                    print(f"ID: {est[0]}, Nombre: {est[1]}, Edad: {est[2]}")
            else:
                print("No hay estudiantes con edad mayor o igual a 18.")

        elif opcion == "7":
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")
        
    db.cerrar_conexion()

if __name__ == "__main__":
    main()