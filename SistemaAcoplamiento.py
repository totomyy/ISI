from Clases import *

class SistemaAcoplamiento:
    def __init__(self, distancia_activacion = 1, tolerancia_distancia = 0.5, tiempo_maximo_espera_seg = 5): 
        self.distancia_activacion = distancia_activacion
        self.tolerancia_distancia = tolerancia_distancia
        self.tiempo_maximo_espera_seg = tiempo_maximo_espera_seg
        self.tiempo_espera_actual = 0

        self.motor_cortina = Motor("Cortina")
        self.motor_rampa = Motor("Rampa")

        self.luz_roja = Luz("rojo")
        self.luz_amarilla = Luz("amarillo")
        self.luz_verde = Luz("verde")

        self.sensor_izq = Sensor("alineacion_izquierda", valor_inicial=False) 
        self.sensor_der = Sensor("alineacion_derecha", valor_inicial=False)
        self.sensor_distancia = Sensor("distancia", valor_inicial=100)

        self.estado_acoplamiento = "INICIO"

    def encender_luz_unica(self, luz_a_encender):
        for luz_actual in [self.luz_roja, self.luz_amarilla, self.luz_verde]:
            if luz_actual == luz_a_encender:
                luz_actual.encender()
            else:
                luz_actual.apagar()

    def verificar_alineacion(self, camion): 
        try:
            alineado_izq_logica = self.sensor_izq.leer()
            alineado_der_logica = self.sensor_der.leer() 

            if not (alineado_izq_logica and alineado_der_logica):
                self.encender_luz_unica(self.luz_roja)
                self.estado_acoplamiento = "ERROR_ALINEACION"
                return False
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja)
            self.estado_acoplamiento = "ERROR_SENSOR_ALINEACION"
            return False

    def verificar_distancia(self, distancia_camion_al_muelle):
        try:
            distancia_sensor_leida = self.sensor_distancia.leer()

            if distancia_sensor_leida <= self.distancia_activacion:
                return True
            else:
                return False

        except Exception as e:
            self.encender_luz_unica(self.luz_roja)
            self.estado_acoplamiento = "ERROR_SENSOR_DISTANCIA"
            return False

    def iniciar_proceso_acoplamiento(self, camion_logica):
        self.estado_acoplamiento = "VERIFICANDO_ALINEACION"
        self.tiempo_espera_actual = 0
        self.sensor_izq.set_valor(camion_logica.alineado_izq)
        self.sensor_der.set_valor(camion_logica.alineado_der)
        self.sensor_distancia.set_valor(camion_logica.distancia_al_muelle)

    def acoplar_camion_paso_a_paso(self, camion_logica, delta_time_seg):
        self.sensor_izq.set_valor(camion_logica.alineado_izq)
        self.sensor_der.set_valor(camion_logica.alineado_der)
        self.sensor_distancia.set_valor(camion_logica.distancia_al_muelle)

        if self.estado_acoplamiento == "VERIFICANDO_ALINEACION":
            if not self.verificar_alineacion(camion_logica): 
                return False 
            self.estado_acoplamiento = "VERIFICANDO_DISTANCIA"
            self.tiempo_espera_actual = 0

        if self.estado_acoplamiento == "VERIFICANDO_DISTANCIA":
            if self.verificar_distancia(camion_logica.distancia_al_muelle):
                self.encender_luz_unica(self.luz_verde)
                self.estado_acoplamiento = "ABRIENDO_CORTINA"
                self.tiempo_espera_actual = 0
            else:
                self.encender_luz_unica(self.luz_roja)
                self.tiempo_espera_actual += delta_time_seg
                if self.tiempo_espera_actual > self.tiempo_maximo_espera_seg:
                    self.estado_acoplamiento = "TIMEOUT_DISTANCIA"
                    self.encender_luz_unica(self.luz_roja)
                    return False
                return True

        TIEMPO_OPERACION_CORTINA = 2
        TIEMPO_OPERACION_RAMPA_LEVANTA = 2
        TIEMPO_OPERACION_RAMPA_BAJA = 1

        if self.estado_acoplamiento == "ABRIENDO_CORTINA":
            self.encender_luz_unica(self.luz_amarilla)
            if not self.motor_cortina.estado:
                self.motor_cortina.activar()
                self.tiempo_espera_actual = 0

            self.tiempo_espera_actual += delta_time_seg
            if self.tiempo_espera_actual >= TIEMPO_OPERACION_CORTINA:
                self.motor_cortina.desactivar()
                self.estado_acoplamiento = "LEVANTANDO_RAMPA"
                self.tiempo_espera_actual = 0
            else:
                return True

        if self.estado_acoplamiento == "LEVANTANDO_RAMPA":
            self.encender_luz_unica(self.luz_amarilla)
            if not self.motor_rampa.estado:
                self.motor_rampa.activar()
                self.tiempo_espera_actual = 0

            self.tiempo_espera_actual += delta_time_seg
            if self.tiempo_espera_actual >= TIEMPO_OPERACION_RAMPA_LEVANTA:
                self.estado_acoplamiento = "BAJANDO_RAMPA"
                self.tiempo_espera_actual = 0
            else:
                return True

        if self.estado_acoplamiento == "BAJANDO_RAMPA":
            self.encender_luz_unica(self.luz_amarilla)
            if not self.motor_rampa.estado:
                pass

            self.tiempo_espera_actual += delta_time_seg
            if self.tiempo_espera_actual >= TIEMPO_OPERACION_RAMPA_BAJA:
                self.motor_rampa.desactivar()
                self.encender_luz_unica(self.luz_verde)
                self.estado_acoplamiento = "ACOPLADO"
                return False
            else:
                return True

        if self.estado_acoplamiento == "ACOPLADO":
            return False

        if "ERROR" in self.estado_acoplamiento or "TIMEOUT" in self.estado_acoplamiento:
            return False

        return True

    def reset_sistema(self):
        self.motor_cortina.desactivar()
        self.motor_rampa.desactivar()
        self.luz_roja.apagar()
        self.luz_amarilla.apagar()
        self.luz_verde.apagar()
        self.sensor_izq.set_valor(False)
        self.sensor_der.set_valor(False)
        self.sensor_distancia.set_valor(100)
        self.estado_acoplamiento = "INICIO"
        self.tiempo_espera_actual = 0
