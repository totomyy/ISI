import time

# Dispositivos simulados

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

        