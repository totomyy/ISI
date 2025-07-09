import time
import pygame

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

pygame.init()

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Simulador de Acoplamiento de Camiones")

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
GRIS = (200, 200, 200)
GRIS_CLARO = (220, 220, 220)
GRIS_OSCURO = (150, 150, 150)
AMARILLO = (255, 255, 0)

RELOJ = pygame.time.Clock()
FPS = 60

class CamionGrafico:
    def __init__(self, x, y, ancho, alto, color=AZUL, id_camion="camion_graf"):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.velocidad_movimiento = 5
        self.id_camion = id_camion
        self.acoplado_a_grafico = None
        self.es_remolque = False

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)
        if self.es_remolque and self.acoplado_a_grafico is None:
            punto_acople_x = self.rect.left + 5
            punto_acople_y = self.rect.centery
            pygame.draw.circle(pantalla, AMARILLO, (punto_acople_x, punto_acople_y), 6)
        elif not self.es_remolque:
            punto_acople_x = self.rect.right - 5
            punto_acople_y = self.rect.centery
            pygame.draw.circle(pantalla, AMARILLO, (punto_acople_x, punto_acople_y), 6)

    def mover(self, dx, dy, pantalla_ancho, pantalla_alto):
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > pantalla_ancho:
            self.rect.right = pantalla_ancho
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > pantalla_alto:
            self.rect.bottom = pantalla_alto

        if self.acoplado_a_grafico and not self.es_remolque:
            self.acoplado_a_grafico.rect.right = self.rect.left - 1
            self.acoplado_a_grafico.rect.centery = self.rect.centery

ANCHO_MUELLE = 100
ALTO_MUELLE = 150
POS_X_MUELLE = ANCHO_PANTALLA - ANCHO_MUELLE
POS_Y_MUELLE = (ALTO_PANTALLA - ALTO_MUELLE) // 2
MUELLE_RECT = pygame.Rect(POS_X_MUELLE, POS_Y_MUELLE, ANCHO_MUELLE, ALTO_MUELLE)

ZONA_ACOPLAMIENTO_RECT = MUELLE_RECT.inflate(20, 20)

camion_principal_grafico = CamionGrafico(50, ALTO_PANTALLA // 2 - 25, 100, 50, color=AZUL, id_camion="Tractor1")

remolque_grafico = CamionGrafico(200, ALTO_PANTALLA // 2 - 25 + 70, 120, 50, color=GRIS, id_camion="Remolque1")
remolque_grafico.es_remolque = True

camion_logica = Camion(id_camion="Tractor1_logic", distancia_inicial=10)

sistema_acoplamiento = SistemaAcoplamiento(distancia_activacion=10, tolerancia_distancia=5, tiempo_maximo_espera_seg=10)

proceso_acoplamiento_activo = False
camion_acoplado_visualmente = False

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if not proceso_acoplamiento_activo and not camion_acoplado_visualmente:
                    distancia_actual_px = MUELLE_RECT.left - camion_principal_grafico.rect.right
                    camion_logica.distancia_al_muelle = max(0, distancia_actual_px)

                    verticalmente_alineado = MUELLE_RECT.top < camion_principal_grafico.rect.centery < MUELLE_RECT.bottom
                    horizontalmente_cerca = ZONA_ACOPLAMIENTO_RECT.colliderect(camion_principal_grafico.rect)

                    esta_alineado_general = verticalmente_alineado and horizontalmente_cerca
                    camion_logica.alineado_izq = esta_alineado_general
                    camion_logica.alineado_der = esta_alineado_general

                    sistema_acoplamiento.reset_sistema()
                    sistema_acoplamiento.iniciar_proceso_acoplamiento(camion_logica)
                    proceso_acoplamiento_activo = True

                elif camion_acoplado_visualmente:
                    camion_principal_grafico.acoplado_a_grafico = None
                    remolque_grafico.acoplado_a_grafico = None
                    camion_acoplado_visualmente = False
                    proceso_acoplamiento_activo = False
                    sistema_acoplamiento.reset_sistema()
                    remolque_grafico.rect.x += 60

    teclas = pygame.key.get_pressed()
    mov_x, mov_y = 0, 0
    if teclas[pygame.K_LEFT]:
        mov_x = -camion_principal_grafico.velocidad_movimiento
    if teclas[pygame.K_RIGHT]:
        mov_x = camion_principal_grafico.velocidad_movimiento
    if teclas[pygame.K_UP]:
        mov_y = -camion_principal_grafico.velocidad_movimiento
    if teclas[pygame.K_DOWN]:
        mov_y = camion_principal_grafico.velocidad_movimiento

    camion_principal_grafico.mover(mov_x, mov_y, ANCHO_PANTALLA, ALTO_PANTALLA)

    if proceso_acoplamiento_activo:
        distancia_actual_px = MUELLE_RECT.left - camion_principal_grafico.rect.right
        camion_logica.distancia_al_muelle = max(0, distancia_actual_px)

        verticalmente_alineado = MUELLE_RECT.top < camion_principal_grafico.rect.centery < MUELLE_RECT.bottom
        dist_y_acople = abs(camion_principal_grafico.rect.centery - MUELLE_RECT.centery)
        TOLERANCIA_ALINEACION_Y = 15

        horizontalmente_listo_para_acoplar = distancia_actual_px < (sistema_acoplamiento.distancia_activacion + 20)

        if dist_y_acople < TOLERANCIA_ALINEACION_Y and horizontalmente_listo_para_acoplar:
            camion_logica.alineado_izq = True
            camion_logica.alineado_der = True
        else:
            camion_logica.alineado_izq = False
            camion_logica.alineado_der = False
            if horizontalmente_listo_para_acoplar and dist_y_acople >= TOLERANCIA_ALINEACION_Y:
                pass

        delta_t = RELOJ.get_time() / 1000.0
        if not sistema_acoplamiento.acoplar_camion_paso_a_paso(camion_logica, delta_t):
            proceso_acoplamiento_activo = False
            if sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
                camion_principal_grafico.acoplado_a_grafico = remolque_grafico
                remolque_grafico.acoplado_a_grafico = camion_principal_grafico
                camion_acoplado_visualmente = True
                remolque_grafico.rect.right = camion_principal_grafico.rect.left -1
                remolque_grafico.rect.centery = camion_principal_grafico.rect.centery

    PANTALLA.fill(BLANCO)

    pygame.draw.rect(PANTALLA, GRIS_CLARO if ZONA_ACOPLAMIENTO_RECT.colliderect(camion_principal_grafico.rect) else GRIS_OSCURO, MUELLE_RECT)
    pygame.draw.rect(PANTALLA, (100,100,100), MUELLE_RECT.inflate(-10,-10))

    LUZ_RADIO = 15
    LUZ_Y = POS_Y_MUELLE - LUZ_RADIO - 10
    LUZ_ROJA_X = POS_X_MUELLE + ANCHO_MUELLE // 4
    LUZ_AMARILLA_X = POS_X_MUELLE + ANCHO_MUELLE // 2
    LUZ_VERDE_X = POS_X_MUELLE + 3 * ANCHO_MUELLE // 4

    color_luz_roja = ROJO if sistema_acoplamiento.luz_roja.encendida else GRIS_OSCURO
    color_luz_amarilla = AMARILLO if sistema_acoplamiento.luz_amarilla.encendida else GRIS_OSCURO
    color_luz_verde = VERDE if sistema_acoplamiento.luz_verde.encendida else GRIS_OSCURO

    pygame.draw.circle(PANTALLA, color_luz_roja, (LUZ_ROJA_X, LUZ_Y), LUZ_RADIO)
    pygame.draw.circle(PANTALLA, color_luz_amarilla, (LUZ_AMARILLA_X, LUZ_Y), LUZ_RADIO)
    pygame.draw.circle(PANTALLA, color_luz_verde, (LUZ_VERDE_X, LUZ_Y), LUZ_RADIO)

    camion_principal_grafico.dibujar(PANTALLA)
    remolque_grafico.dibujar(PANTALLA)

    FUENTE_TEXTO = pygame.font.Font(None, 28)

    texto_instrucciones = FUENTE_TEXTO.render("Mover: Flechas | Acoplar/Desacoplar: ESPACIO", True, NEGRO)
    PANTALLA.blit(texto_instrucciones, (10, 10))

    estado_texto_str = f"Estado Sistema: {sistema_acoplamiento.estado_acoplamiento}"
    if proceso_acoplamiento_activo and sistema_acoplamiento.estado_acoplamiento == "VERIFICANDO_DISTANCIA":
        tiempo_restante = max(0, sistema_acoplamiento.tiempo_maximo_espera_seg - sistema_acoplamiento.tiempo_espera_actual)
        estado_texto_str += f" (Esperando {tiempo_restante:.1f}s)"
    elif camion_acoplado_visualmente and sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
        estado_texto_str = "Estado Sistema: CAMION ACOPLADO"

    texto_estado_sistema = FUENTE_TEXTO.render(estado_texto_str, True, NEGRO)
    PANTALLA.blit(texto_estado_sistema, (10, 40))

    texto_cortina_rampa_str = f"Cortina: {'abierta' if sistema_acoplamiento.motor_cortina.estado or sistema_acoplamiento.estado_acoplamiento == 'ACOPLADO' else 'cerrada'}"
    texto_cortina_rampa_str += f", Rampa: {'extendida/en uso' if (sistema_acoplamiento.motor_rampa.estado or sistema_acoplamiento.estado_acoplamiento == 'ACOPLADO') else 'retraida'}"

    if sistema_acoplamiento.estado_acoplamiento == "ABRIENDO_CORTINA":
        texto_cortina_rampa_str += " (Abriendo cortina...)"
    elif sistema_acoplamiento.estado_acoplamiento == "LEVANTANDO_RAMPA":
        texto_cortina_rampa_str += " (Levantando rampa...)"
    elif sistema_acoplamiento.estado_acoplamiento == "BAJANDO_RAMPA":
        texto_cortina_rampa_str += " (Bajando rampa a posición...)"

    texto_cortina_rampa_render = FUENTE_TEXTO.render(texto_cortina_rampa_str, True, NEGRO)
    PANTALLA.blit(texto_cortina_rampa_render, (10, 70))

    CORTINA_COLOR = (100, 100, 120)
    cortina_max_h = MUELLE_RECT.height - 10
    cortina_h = cortina_max_h
    cortina_y = MUELLE_RECT.top + 5

    if sistema_acoplamiento.estado_acoplamiento == "ABRIENDO_CORTINA":
        progreso_apertura = sistema_acoplamiento.tiempo_espera_actual / 2.0
        cortina_h = max(0, cortina_max_h * (1 - progreso_apertura))
        cortina_y = (MUELLE_RECT.top + 5) + (cortina_max_h - cortina_h)
    elif sistema_acoplamiento.motor_cortina.estado or \
         sistema_acoplamiento.estado_acoplamiento in ["LEVANTANDO_RAMPA", "BAJANDO_RAMPA", "ACOPLADO"]:
        cortina_h = 0

    if cortina_h > 0:
        cortina_rect = pygame.Rect(MUELLE_RECT.left + 5, cortina_y, MUELLE_RECT.width - 10, cortina_h)
        pygame.draw.rect(PANTALLA, CORTINA_COLOR, cortina_rect)

    RAMPA_COLOR = (120, 120, 100)
    rampa_w = MUELLE_RECT.width - 20
    rampa_h_max = 40
    rampa_h = 0
    rampa_x = MUELLE_RECT.left + 10
    rampa_y = MUELLE_RECT.centery - 10

    if sistema_acoplamiento.estado_acoplamiento == "LEVANTANDO_RAMPA":
        progreso_levante = sistema_acoplamiento.tiempo_espera_actual / 2.0
        rampa_h = min(rampa_h_max, rampa_h_max * progreso_levante)
        rampa_rect = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect)
    elif sistema_acoplamiento.estado_acoplamiento == "BAJANDO_RAMPA":
        rampa_h = rampa_h_max
        rampa_rect = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect)
    elif sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
        rampa_h = rampa_h_max
        rampa_rect = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect)

    pygame.display.flip()

    RELOJ.tick(FPS)

pygame.quit()