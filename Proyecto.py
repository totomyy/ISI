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


# Camion


class Camion:
    def __init__(self, id_camion, distancia_inicial, alineado_izq=True, alineado_der=True):
        self.id = id_camion
        self.distancia = distancia_inicial
        self.alineado_izq = alineado_izq
        self.alineado_der = alineado_der

    def acercarse(self, metros):
        if metros < 0:
            raise ValueError("La distancia a avanzar debe ser positiva.")
        self.distancia = max (0, self.distancia - metros)

    def esta_alineado(self):
        return self.alineado_izq and self.alineado_der
    

# Sistema de Acoplamiento


class SistemaAcoplamiento:
    def __init__(self, distancia_activacion = 1, tolerancia_distancia = 0.5, tiempo_maximo_espera = 15):
        self.distancia_activacion = distancia_activacion
        self.tolerancia_distancia = tolerancia_distancia
        self.tiempo_maximo_espera = tiempo_maximo_espera

        # Componentes fisicos
        self.motor_cortina = Motor("Cortina")
        self.motor_rampa = Motor("Rampa")

        self.luz_roja = Luz("rojo")
        self.luz_amarilla = Luz("amarillo")
        self.luz_verde = Luz("verde")

        self.sensor_izq = Sensor("alineacion_izquierda")
        self.sensor_der = Sensor("alineacion_derecha")
        self.sensor_distancia = Sensor("distancia")

    def encender_luz_unica(self, luz):
        for i in [self.luz_roja, self.luz_amarilla, self.luz_verde]:
            i.apagar()
        luz.encender()

    def verificar_alineacion(self, camion):
        try:
            alineado_izq = camion.alineado_izq and self.sensor_izq.leer()
            alineado_der = camion.alineado_der and self.sensor_der.leer()
            if not (alineado_izq and alineado_der):
                self.encender_luz_unica(self.luz_roja)
                print("[ALERTA] Camion desalineado. Solicitar corrección manual.")
                return False
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja)
            print(f"[ERROR] Fallo en sensores de alineacion: {e}")
            return False
        