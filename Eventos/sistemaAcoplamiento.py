import time
import datetime
from clases import *

# Sistema de Acoplamiento

class SistemaAcoplamiento:
    UMBRAL_TAMANO_MINIMO_OBJETO = 10  
    TOLERANCIA_DESNIVEL_MAXIMA_CM = 5 
    NOMBRE_ARCHIVO_LOG = "eventos_acoplamiento.log" 

    def __init__(self, distancia_activacion=1, tolerancia_distancia=0.5, tiempo_maximo_espera=15):
        self.distancia_activacion = distancia_activacion
        self.tolerancia_distancia = tolerancia_distancia
        self.tiempo_maximo_espera = tiempo_maximo_espera
        
        self.motor_cortina = Motor("Cortina")
        self.motor_rampa = Motor("Rampa")

        self.luz_roja = Luz("rojo")
        self.luz_amarilla = Luz("amarillo")
        self.luz_verde = Luz("verde")

        self.sensor_izq = Sensor("alineacion_izquierda")
        self.sensor_der = Sensor("alineacion_derecha")
        self.sensor_distancia = Sensor("distancia")
        self.sensor_tamano_objeto = Sensor("tamano_objeto") 

       
        with open(self.NOMBRE_ARCHIVO_LOG, "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} [SISTEMA] Sistema de acoplamiento inicializado.\n")

    def registrar_evento(self, mensaje, nivel="INFO", id_camion=None):
        """Registra un evento en la consola y en el archivo de log."""
        timestamp = datetime.datetime.now().isoformat()
        prefijo_camion = f"[Camión {id_camion}] " if id_camion else ""
        mensaje_completo = f"{timestamp} [{nivel.upper()}] {prefijo_camion}{mensaje}"

        print(mensaje_completo) 
        try:
            with open(self.NOMBRE_ARCHIVO_LOG, "a") as f:
                f.write(mensaje_completo + "\n")
        except Exception as e:
            print(f"{timestamp} [ERROR_INTERNO] No se pudo escribir en el archivo de log: {e}")

    def encender_luz_unica(self, luz_a_encender, id_camion=None):
        
        for luz_actual in [self.luz_roja, self.luz_amarilla, self.luz_verde]:
            if luz_actual.estado:
                luz_actual.apagar()
                self.registrar_evento(f"Luz {luz_actual.color.upper()} apagada.", "DEBUG", id_camion)

        
        if luz_a_encender:
            if not luz_a_encender.estado:
                luz_a_encender.encender()
                self.registrar_evento(f"Luz {luz_a_encender.color.upper()} encendida.", "INFO", id_camion)

    
    def verificar_tamano_objeto(self, tamano_objeto_detectado, id_camion=None):
        """Verifica si el objeto detectado es suficientemente grande."""
        self.registrar_evento(f"Verificando tamaño del objeto: {tamano_objeto_detectado}", "DEBUG", id_camion)
        if tamano_objeto_detectado < self.UMBRAL_TAMANO_MINIMO_OBJETO:
            self.registrar_evento(f"RF-1.1: Objeto pequeño detectado (tamaño: {tamano_objeto_detectado}). Ignorando aproximación.", "ALERTA", id_camion)
            return False
        self.registrar_evento(f"RF-1.1: Objeto de tamaño adecuado detectado (tamaño: {tamano_objeto_detectado}).", "INFO", id_camion)
        return True

    
    def verificar_desnivel(self, camion):
        """Verifica si el desnivel del camión está dentro de la tolerancia."""
        self.registrar_evento(f"Verificando desnivel del camión: {camion.desnivel_cm}cm", "DEBUG", camion.id)
        if abs(camion.desnivel_cm) > self.TOLERANCIA_DESNIVEL_MAXIMA_CM:
            self.registrar_evento(f"RF-3.1: Desnivel del camión ({camion.desnivel_cm}cm) excede la tolerancia ({self.TOLERANCIA_DESNIVEL_MAXIMA_CM}cm).", "ALERTA", camion.id)
            
            return True 
        self.registrar_evento(f"RF-3.1: Desnivel del camión ({camion.desnivel_cm}cm) dentro de la tolerancia.", "INFO", camion.id)
        return True

    def verificar_alineacion(self, camion):
        try:
            self.sensor_izq.set_valor(camion.alineado_izq) 
            self.sensor_der.set_valor(camion.alineado_der) 

            alineado_izq_sensor = self.sensor_izq.leer() 
            alineado_der_sensor = self.sensor_der.leer()
            
            if not (alineado_izq_sensor and alineado_der_sensor):
                self.encender_luz_unica(self.luz_roja, camion.id)
                self.registrar_evento("Camión desalineado según sensores. Solicitar corrección manual.", "ALERTA", camion.id)
                return False
            self.registrar_evento("Camión alineado según sensores.", "INFO", camion.id)
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, camion.id)
            self.registrar_evento(f"Fallo en sensores de alineación: {e}", "ERROR", camion.id)
            return False

    def verificar_distancia(self, camion): 
        try:
            self.sensor_distancia.set_valor(camion.distancia) 
            distancia_medida_sensor = self.sensor_distancia.leer()
            
            if distancia_medida_sensor <= self.distancia_activacion:
                return True
            else:
                return False
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, camion.id)
            self.registrar_evento(f"Sensor de distancia defectuoso: {e}", "ERROR", camion.id)
            return False

    def acoplar_camion(self, camion):
        self.registrar_evento(f"Iniciando proceso de acoplamiento.", "INFO", camion.id)
        
        
        self.sensor_tamano_objeto.set_valor(camion.tamano) 
        tamano_detectado = self.sensor_tamano_objeto.leer()
        if not self.verificar_tamano_objeto(tamano_detectado, camion.id):
            self.encender_luz_unica(self.luz_roja, camion.id)
            return False 

        if not self.verificar_alineacion(camion):
            
            return False

        self.encender_luz_unica(self.luz_amarilla, camion.id)
        self.registrar_evento("Camión alineado y de tamaño correcto. Esperando posicionamiento...", "INFO", camion.id)

        tiempo_espera = 0
        self.sensor_distancia.set_valor(camion.distancia)

        while not self.verificar_distancia(camion): 
            
            
            if self.sensor_distancia.activo: 
                 self.encender_luz_unica(self.luz_roja, camion.id)

            self.registrar_evento(f"Camión a {camion.distancia:.1f}m. Objetivo: <= {self.distancia_activacion}m. Esperando avance...", "INFO", camion.id)
            
            time.sleep(1) 
            tiempo_espera += 1
            
            if tiempo_espera > self.tiempo_maximo_espera:
                self.registrar_evento(f"Tiempo de espera ({self.tiempo_maximo_espera}s) excedido. Abortando operación.", "ERROR", camion.id)
                self.encender_luz_unica(self.luz_roja, camion.id)
                return False

            if camion.distancia > self.distancia_activacion:
                 camion.acercarse(0.5) 
                 self.sensor_distancia.set_valor(camion.distancia) 
                 self.registrar_evento(f"Camión avanza a {camion.distancia:.1f}m.", "DEBUG", camion.id)
            elif camion.distancia < 0: 
                 self.registrar_evento("Distancia de camión negativa en simulación.", "ERROR", camion.id)
                 self.encender_luz_unica(self.luz_roja, camion.id)
                 return False

        self.encender_luz_unica(self.luz_verde, camion.id)
        self.registrar_evento(f"Camión en posición adecuada ({camion.distancia:.1f}m).", "INFO", camion.id)

        
        if not self.verificar_desnivel(camion):
            
            pass

        if not self.abrir_cortina(camion.id):
            return False
        
        if not self.operar_rampa_acoplamiento(camion): 
            return False

        self.encender_luz_unica(self.luz_verde, camion.id)
        self.registrar_evento(f"Camión acoplado correctamente.", "INFO", camion.id)
        return True

    def abrir_cortina(self, id_camion=None, cerrar=False):
        accion = "Cerrando" if cerrar else "Abriendo"
        estado_final_motor = False if cerrar else True 

        try:
            self.registrar_evento(f"{accion} cortina...", "INFO", id_camion)
            self.encender_luz_unica(self.luz_amarilla, id_camion)
            
            self.motor_cortina.activar()
            self.registrar_evento(f"Motor {self.motor_cortina.nombre} activado para {accion.lower()} cortina.", "DEBUG", id_camion)
            time.sleep(2) 
            self.motor_cortina.desactivar()
            self.registrar_evento(f"Motor {self.motor_cortina.nombre} desactivado.", "DEBUG", id_camion)
            self.registrar_evento(f"Cortina {'cerrada' if cerrar else 'abierta'}.", "INFO", id_camion)
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, id_camion)
            self.registrar_evento(f"Fallo al {'cerrar' if cerrar else 'abrir'} la cortina: {e}", "ERROR", id_camion)
            return False

    def operar_rampa_acoplamiento(self, camion):
        """Maneja la secuencia de levantar y bajar la rampa para acoplar."""
        
        try:
            self.registrar_evento("Levantando rampa...", "INFO", camion.id)
            self.encender_luz_unica(self.luz_amarilla, camion.id)
            self.motor_rampa.activar()
            self.registrar_evento(f"Motor {self.motor_rampa.nombre} activado para levantar rampa.", "DEBUG", camion.id)
            time.sleep(2) 
            
            self.registrar_evento("Rampa levantada.", "INFO", camion.id)
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, camion.id)
            self.registrar_evento(f"Fallo al levantar rampa: {e}", "ERROR", camion.id)
            
            if self.motor_rampa.estado: self.motor_rampa.desactivar() 
            return False

        
        try:
            self.registrar_evento("Bajando rampa sobre el camión...", "INFO", camion.id)
            self.encender_luz_unica(self.luz_amarilla, camion.id) 
            time.sleep(1) 
            self.motor_rampa.desactivar() 
            self.registrar_evento(f"Motor {self.motor_rampa.nombre} desactivado, rampa bajada.", "DEBUG", camion.id)
            self.registrar_evento("Rampa bajada y posicionada.", "INFO", camion.id)
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, camion.id)
            self.registrar_evento(f"Fallo al bajar rampa: {e}", "ERROR", camion.id)
            return False

    def operar_rampa_desacoplamiento(self, id_camion=None):
        """Maneja la secuencia de retraer/subir la rampa para desacoplar."""
        
        try:
            self.registrar_evento("Retrayendo/subiendo rampa...", "INFO", id_camion)
            self.encender_luz_unica(self.luz_amarilla, id_camion)
            self.motor_rampa.activar() 
            self.registrar_evento(f"Motor {self.motor_rampa.nombre} activado para retraer rampa.", "DEBUG", id_camion)
            time.sleep(2) 
            self.motor_rampa.desactivar() 
            self.registrar_evento(f"Motor {self.motor_rampa.nombre} desactivado.", "DEBUG", id_camion)
            self.registrar_evento("Rampa retraída/subida.", "INFO", id_camion)
            return True
        except Exception as e:
            self.encender_luz_unica(self.luz_roja, id_camion)
            self.registrar_evento(f"Fallo al retraer/subir la rampa: {e}", "ERROR", id_camion)
            return False

    
    def secuencia_cierre(self, camion):
        self.registrar_evento("Iniciando secuencia de cierre automático / desacoplamiento.", "INFO", camion.id)

        
        if self.motor_rampa.estado: 
             pass 

        self.registrar_evento("Verificando estado de la rampa antes de operar para cierre.", "DEBUG", camion.id)
        
        if not self.operar_rampa_desacoplamiento(camion.id):
            self.registrar_evento("Fallo crítico en operación de rampa durante cierre. Abortando parcialmente.", "ERROR", camion.id)
            
            pass 

        
        if not self.abrir_cortina(camion.id, cerrar=True): 
            self.registrar_evento("Fallo crítico en cierre de cortina. Revisar manualmente.", "ERROR", camion.id)
           
            pass

        
        self.encender_luz_unica(self.luz_roja, camion.id) 
        self.registrar_evento("Secuencia de cierre completada. Muelle asegurado. Camión puede retirarse.", "INFO", camion.id)

        
        if self.motor_cortina.estado: self.motor_cortina.desactivar()
        if self.motor_rampa.estado: self.motor_rampa.desactivar()

        return True