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