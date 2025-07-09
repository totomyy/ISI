class Motor:
    def __init__(self, nombre):
        self.nombre = nombre
        self.estado = False 

    def activar(self):
        self.estado = True

    def desactivar(self):
        self.estado = False

class Luz:
    def __init__(self, color):
        self.color = color
        self.encendida = False 

    def encender(self):
        self.encendida = True

    def apagar(self):
        self.encendida = False

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

class Camion: 
    def __init__(self, id_camion, distancia_inicial, alineado_izq=True, alineado_der=True):
        self.id = id_camion
        self.x = 0 
        self.y = 0 
        self.distancia_al_muelle = distancia_inicial 
        self.alineado_izq = alineado_izq
        self.alineado_der = alineado_der
        self.acoplado_a = None 

    def acercarse(self, metros): 
        if metros < 0:
            raise ValueError("La distancia a avanzar debe ser positiva.")
        self.distancia_al_muelle = max (0, self.distancia_al_muelle - metros)

    def esta_alineado(self):
        return self.alineado_izq and self.alineado_der