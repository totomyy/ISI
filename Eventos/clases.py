import time
import datetime

class Motor:
    def __init__(self, nombre):
        self.nombre = nombre
        self.estado = False  

    def activar(self):
        self.estado = True
        print(f"[INFO] Motor {self.nombre} activado.")

    def desactivar(self):
        self.estado = False
        print(f"[INFO] Motor {self.nombre} desactivado.")

class Luz:
    def __init__(self, color):
        self.color = color
        self.estado = False  

    def encender(self):
        self.estado = True
        print(f"[INFO] Luz {self.color.upper()} encendida.")

    def apagar(self):
        self.estado = False
        print(f"[INFO] Luz {self.color.upper()} apagada.")

class Sensor:
    def __init__(self, nombre, valor_inicial=0):
        self.nombre = nombre
        self.valor = valor_inicial
        self.activo = True

    def leer(self):
        if not self.activo:
            raise Exception(f"[ERROR] Sensor {self.nombre} no responde.")
        return self.valor

    def set_valor(self, valor):
        self.valor = valor

    def desactivar(self):
        self.activo = False

# Camion

class Camion:
    def __init__(self, id_camion, distancia_inicial, tamano=20, alineado_izq=True, alineado_der=True, desnivel_cm=0): # RF-1.1: Añadido tamano, RF-3.1: Añadido desnivel_cm
        self.id = id_camion
        self.distancia = distancia_inicial
        self.tamano = tamano 
        self.alineado_izq = alineado_izq
        self.alineado_der = alineado_der
        self.desnivel_cm = desnivel_cm 

    def acercarse(self, metros):
        if metros < 0:
            raise ValueError("La distancia a avanzar debe ser positiva.")
        self.distancia = max (0, self.distancia - metros)

    def esta_alineado(self):
        return self.alineado_izq and self.alineado_der