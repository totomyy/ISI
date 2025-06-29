from Clases import *
import time

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
        
    def verificar_distancia(self, distancia_actual):
        try:
            distancia_sensor = self.sensor_distancia.leer()
            diferencia = abs(distancia_actual - distancia_sensor)
            if diferencia > self.tolerancia_distancia:
                raise ValueError("Diferencia entre sensor y distancia esperada supera la tolerancia.")
            return distancia_sensor <= self.distancia_activacion
        except Exception as e:
            self.encender_luz_unica(self.luz_roja)
            print(f"[ERROR] Sensor de distancia defectuoso: {e}")
            return False

    def acoplar_camion(self, camion):
        print(f"[INFO] Iniciando acoplamiento del camion {camion.id}...")

        if not self.verificar_alineacion(camion):
            return
        
        tiempo_espera = 0
        while not self.verificar_distancia(camion.distancia):
            self.encender_luz_unica(self.luz_roja)
            print("[INFO] Camion aun no esta en posicion. Esperando avance...")
            time.sleep(1)
            tiempo_espera += 1
            if tiempo_espera > self.tiempo_maximo_espera:
                print("[ERROR] Tiempo de espera excedido. Abortando operacion.")
                return
            camion.acercarse(0.5)
            self.sensor_distancia.set_valor(camion.distancia)
        
        self.encender_luz_unica(self.luz_verde)
        print("[INFO] Camion en posicion adecuada.")

        if not self.abrir_cortina():
            return
        if not self.levantar_rampa():
            return
        if not self.bajar_rampa():
            return
        
        self.encender_luz_unica(self.luz_verde)
        print(f"[INFO] Camion {camion.id} acoplado correctamente.")

    def abrir_cortina(self):
        try:
            self.encender_luz_unica(self.luz_amarilla)
            self.motor_cortina.activar()
            time.sleep(2)
            self.motor_cortina.desactivar()
            return True
        except Exception as e:
            print(f"[ERROR] Fallo al abrir la cortina: {e}")
            return False
        
    def levantar_rampa(self):
        try:
            self.encender_luz_unica(self.luz_amarilla)
            self.motor_rampa.activar()
            time.sleep(2)
            return True
        except Exception as e:
            print(f"[ERROR] Fallo al levantar rampa: {e}")
            return False
        
    def bajar_rampa(self):
        try:
            time.sleep(1)
            self.motor_rampa.desactivar()
            return True
        except Exception as e:
            print(f"[ERROR] Fallo al bajar rampa: {e}")
            return False