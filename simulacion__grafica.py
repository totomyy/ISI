import time
import pygame
from Clases import *
from SistemaAcoplamiento import *

pygame.init()

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Simulador de Acoplamiento de Camiones")

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (200, 0, 0)
VERDE = (0, 200, 0)
AMARILLO = (200, 200, 0)
AZUL_CAMION = (50, 80, 150)
GRIS_REMOLQUE = (100, 100, 100)
COLOR_ASFALTO = (50, 50, 60)
COLOR_CONCRETO = (100, 100, 100)
COLOR_CONCRETO_CLARO = (120, 120, 120)
COLOR_CONCRETO_OSCURO = (80, 80, 80)
COLOR_LINEA_CARRETERA = (200, 200, 0)
COLOR_BORDE = (20, 20, 20)

RELOJ = pygame.time.Clock()
FPS = 60
TOLERANCIA_ALINEACION_Y = 15

class CamionGrafico:
    def __init__(self, x, y, ancho, alto, color=AZUL_CAMION, id_camion="camion_graf"):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.velocidad_movimiento = 5
        self.id_camion = id_camion
        self.acoplado_a_grafico = None
        self.es_remolque = False

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2)

        if not self.es_remolque:
            ancho_cabina = self.rect.width // 3
            alto_cabina = self.rect.height - 4
            cabina_rect = pygame.Rect(self.rect.left + 2, self.rect.top + 2, ancho_cabina, alto_cabina)
            pygame.draw.rect(pantalla, self.color, cabina_rect)
            pygame.draw.rect(pantalla, COLOR_BORDE, cabina_rect, 1)

            if not self.acoplado_a_grafico:
                punto_acople_x = self.rect.right - 7
                punto_acople_y = self.rect.centery
                pygame.draw.circle(pantalla, AMARILLO, (punto_acople_x, punto_acople_y), 5)
                pygame.draw.circle(pantalla, COLOR_BORDE, (punto_acople_x, punto_acople_y), 5, 1)

        elif self.es_remolque:
            if self.acoplado_a_grafico is None:
                punto_acople_x = self.rect.left + 7
                punto_acople_y = self.rect.centery
                pygame.draw.circle(pantalla, AMARILLO, (punto_acople_x, punto_acople_y), 5)
                pygame.draw.circle(pantalla, COLOR_BORDE, (punto_acople_x, punto_acople_y), 5, 1)

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

class Muelle:
    def __init__(self, x, y, ancho, alto, color_exterior=COLOR_CONCRETO, color_interior=COLOR_CONCRETO_OSCURO, color_zona_activa=COLOR_CONCRETO_CLARO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_exterior = color_exterior
        self.color_interior = color_interior
        self.color_zona_activa = color_zona_activa
        self.zona_acoplamiento_rect = self.rect.inflate(20, 20)

    def dibujar(self, pantalla, camion_rect_opcional=None):
        current_exterior_color = self.color_exterior
        if camion_rect_opcional and self.zona_acoplamiento_rect.colliderect(camion_rect_opcional):
            current_exterior_color = self.color_zona_activa

        pygame.draw.rect(pantalla, current_exterior_color, self.rect)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2)
        pygame.draw.rect(pantalla, self.color_interior, self.rect.inflate(-10, -10))

    def get_zona_acoplamiento_rect(self):
        return self.zona_acoplamiento_rect

    def get_rect(self):
        return self.rect

ANCHO_MUELLE_CONST = 100
ALTO_MUELLE_CONST = 150
POS_X_MUELLE_CONST = ANCHO_PANTALLA - ANCHO_MUELLE_CONST
POS_Y_MUELLE_CONST = (ALTO_PANTALLA - ALTO_MUELLE_CONST) // 2
muelle_obj = Muelle(POS_X_MUELLE_CONST, POS_Y_MUELLE_CONST, ANCHO_MUELLE_CONST, ALTO_MUELLE_CONST)

camion_principal_grafico = CamionGrafico(170, ALTO_PANTALLA // 2 - 25, 100, 50, color=AZUL_CAMION, id_camion="Tractor1")
remolque_grafico = CamionGrafico(0, 0, 120, 50, color=GRIS_REMOLQUE, id_camion="Remolque1")
remolque_grafico.es_remolque = True

camion_principal_grafico.acoplado_a_grafico = remolque_grafico
remolque_grafico.acoplado_a_grafico = camion_principal_grafico
remolque_grafico.rect.right = camion_principal_grafico.rect.left -1
remolque_grafico.rect.centery = camion_principal_grafico.rect.centery

camion_logica = Camion(id_camion="Tractor1_logic", distancia_inicial=10)
sistema_acoplamiento = SistemaAcoplamiento(distancia_activacion=10, tolerancia_distancia=5, tiempo_maximo_espera_seg=10)

proceso_acoplamiento_activo = False
esta_camion_remolque_acoplado_al_muelle = False

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if not proceso_acoplamiento_activo and not esta_camion_remolque_acoplado_al_muelle:
                    distancia_actual_px = muelle_obj.get_rect().left - remolque_grafico.rect.right
                    camion_logica.distancia_al_muelle = max(0, distancia_actual_px)

                    verticalmente_alineado = muelle_obj.get_rect().top < remolque_grafico.rect.centery < muelle_obj.get_rect().bottom
                    horizontalmente_cerca = muelle_obj.get_zona_acoplamiento_rect().colliderect(remolque_grafico.rect)

                    esta_alineado_general = verticalmente_alineado and horizontalmente_cerca
                    camion_logica.alineado_izq = esta_alineado_general
                    camion_logica.alineado_der = esta_alineado_general

                    sistema_acoplamiento.reset_sistema()
                    sistema_acoplamiento.iniciar_proceso_acoplamiento(camion_logica)
                    proceso_acoplamiento_activo = True

                elif esta_camion_remolque_acoplado_al_muelle and not proceso_acoplamiento_activo:
                    esta_camion_remolque_acoplado_al_muelle = False
                    sistema_acoplamiento.reset_sistema()

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
        distancia_actual_px = muelle_obj.get_rect().left - remolque_grafico.rect.right
        camion_logica.distancia_al_muelle = max(0, distancia_actual_px)

        dist_y_acople = abs(remolque_grafico.rect.centery - muelle_obj.get_rect().centery)
        horizontalmente_listo_para_acoplar = distancia_actual_px < (sistema_acoplamiento.distancia_activacion + 40)

        if dist_y_acople < TOLERANCIA_ALINEACION_Y and horizontalmente_listo_para_acoplar:
            camion_logica.alineado_izq = True
            camion_logica.alineado_der = True
        else:
            camion_logica.alineado_izq = False
            camion_logica.alineado_der = False

        delta_t = RELOJ.get_time() / 1000.0
        if not sistema_acoplamiento.acoplar_camion_paso_a_paso(camion_logica, delta_t):
            proceso_acoplamiento_activo = False
            if sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
                esta_camion_remolque_acoplado_al_muelle = True

    PANTALLA.fill(COLOR_ASFALTO)

    alto_edificio = 60
    color_edificio = (30, 30, 40)
    pygame.draw.rect(PANTALLA, color_edificio, (0, 0, ANCHO_PANTALLA, alto_edificio))
    pygame.draw.rect(PANTALLA, NEGRO, (0, 0, ANCHO_PANTALLA, alto_edificio), 2)
    pygame.draw.rect(PANTALLA, color_edificio, (0, ALTO_PANTALLA - alto_edificio, ANCHO_PANTALLA, alto_edificio))
    pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO_PANTALLA - alto_edificio, ANCHO_PANTALLA, alto_edificio), 2)

    largo_segmento_linea = 40
    espacio_segmento_linea = 25
    ancho_linea_carretera = 5
    area_maniobra_ancho = ANCHO_PANTALLA - muelle_obj.get_rect().width
    pos_x_linea_central = area_maniobra_ancho // 3

    for y_segmento in range(0, ALTO_PANTALLA, largo_segmento_linea + espacio_segmento_linea):
        pygame.draw.rect(PANTALLA, COLOR_LINEA_CARRETERA,
                         (pos_x_linea_central - ancho_linea_carretera // 2, y_segmento,
                          ancho_linea_carretera, largo_segmento_linea))

    muelle_obj.dibujar(PANTALLA, camion_principal_grafico.rect)

    if not proceso_acoplamiento_activo and not esta_camion_remolque_acoplado_al_muelle:
        muelle_rect_actual = muelle_obj.get_rect()
        guia_alto = TOLERANCIA_ALINEACION_Y * 2
        guia_ancho = 20
        guia_x = muelle_rect_actual.left - guia_ancho - 5
        guia_y = muelle_rect_actual.centery - TOLERANCIA_ALINEACION_Y

        guia_color = (0, 100, 0, 100)

        dist_y_acople_guia = abs(remolque_grafico.rect.centery - muelle_rect_actual.centery)
        esta_verticalmente_alineado_guia = dist_y_acople_guia < TOLERANCIA_ALINEACION_Y

        esta_horizontalmente_cerca_guia = muelle_obj.get_zona_acoplamiento_rect().collidepoint(remolque_grafico.rect.right, remolque_grafico.rect.centery)

        distancia_actual_al_muelle_px = muelle_rect_actual.left - remolque_grafico.rect.right
        esta_a_distancia_perfecta = distancia_actual_al_muelle_px <= sistema_acoplamiento.distancia_activacion and distancia_actual_al_muelle_px >= 0

        if esta_verticalmente_alineado_guia and esta_horizontalmente_cerca_guia:
            if esta_a_distancia_perfecta:
                guia_color = (0, 255, 0, 200)
            else:
                guia_color = (0, 200, 0, 150)

        guia_surface = pygame.Surface((guia_ancho, guia_alto), pygame.SRCALPHA)
        guia_surface.fill(guia_color)
        PANTALLA.blit(guia_surface, (guia_x, guia_y))

        borde_color_guia = (255, 255, 255, 150)
        if esta_verticalmente_alineado_guia and esta_horizontalmente_cerca_guia and esta_a_distancia_perfecta:
            borde_color_guia = (255, 255, 0, 200)

        pygame.draw.rect(PANTALLA, borde_color_guia, (guia_x, guia_y, guia_ancho, guia_alto), 2)

    LUZ_RADIO = 15
    LUZ_Y = POS_Y_MUELLE_CONST - LUZ_RADIO - 10
    LUZ_ROJA_X = POS_X_MUELLE_CONST + ANCHO_MUELLE_CONST // 4
    LUZ_AMARILLA_X = POS_X_MUELLE_CONST + ANCHO_MUELLE_CONST // 2
    LUZ_VERDE_X = POS_X_MUELLE_CONST + 3 * ANCHO_MUELLE_CONST // 4

    luz_apagada_color = COLOR_CONCRETO_OSCURO
    color_luz_roja = ROJO if sistema_acoplamiento.luz_roja.encendida else luz_apagada_color
    color_luz_amarilla = AMARILLO if sistema_acoplamiento.luz_amarilla.encendida else luz_apagada_color
    color_luz_verde = VERDE if sistema_acoplamiento.luz_verde.encendida else luz_apagada_color

    pygame.draw.circle(PANTALLA, color_luz_roja, (LUZ_ROJA_X, LUZ_Y), LUZ_RADIO)
    pygame.draw.circle(PANTALLA, COLOR_BORDE, (LUZ_ROJA_X, LUZ_Y), LUZ_RADIO, 1)
    pygame.draw.circle(PANTALLA, color_luz_amarilla, (LUZ_AMARILLA_X, LUZ_Y), LUZ_RADIO)
    pygame.draw.circle(PANTALLA, COLOR_BORDE, (LUZ_AMARILLA_X, LUZ_Y), LUZ_RADIO, 1)
    pygame.draw.circle(PANTALLA, color_luz_verde, (LUZ_VERDE_X, LUZ_Y), LUZ_RADIO)
    pygame.draw.circle(PANTALLA, COLOR_BORDE, (LUZ_VERDE_X, LUZ_Y), LUZ_RADIO, 1)

    camion_principal_grafico.dibujar(PANTALLA)
    remolque_grafico.dibujar(PANTALLA)

    FUENTE_TEXTO = pygame.font.Font(None, 28)
    COLOR_TEXTO = BLANCO

    texto_instrucciones = FUENTE_TEXTO.render("Mover: Flechas | Acoplar/Desacoplar: ESPACIO", True, COLOR_TEXTO)
    PANTALLA.blit(texto_instrucciones, (10, 10))

    estado_texto_str = f"Estado Sistema: {sistema_acoplamiento.estado_acoplamiento}"
    if proceso_acoplamiento_activo and sistema_acoplamiento.estado_acoplamiento == "VERIFICANDO_DISTANCIA":
        tiempo_restante = max(0, sistema_acoplamiento.tiempo_maximo_espera_seg - sistema_acoplamiento.tiempo_espera_actual)
        estado_texto_str += f" (Esperando {tiempo_restante:.1f}s)"
    elif esta_camion_remolque_acoplado_al_muelle and sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
        estado_texto_str = "Estado Sistema: REMOLQUE ACOPLADO AL MUELLE"

    texto_estado_sistema = FUENTE_TEXTO.render(estado_texto_str, True, COLOR_TEXTO)
    PANTALLA.blit(texto_estado_sistema, (10, 40))

    texto_cortina_rampa_str = f"Cortina: {'abierta' if sistema_acoplamiento.motor_cortina.estado or sistema_acoplamiento.estado_acoplamiento == 'ACOPLADO' else 'cerrada'}"
    texto_cortina_rampa_str += f", Rampa: {'extendida/en uso' if (sistema_acoplamiento.motor_rampa.estado or sistema_acoplamiento.estado_acoplamiento == 'ACOPLADO') else 'retraida'}"

    if sistema_acoplamiento.estado_acoplamiento == "ABRIENDO_CORTINA":
        texto_cortina_rampa_str += " (Abriendo cortina...)"
    elif sistema_acoplamiento.estado_acoplamiento == "LEVANTANDO_RAMPA":
        texto_cortina_rampa_str += " (Levantando rampa...)"
    elif sistema_acoplamiento.estado_acoplamiento == "BAJANDO_RAMPA":
        texto_cortina_rampa_str += " (Bajando rampa a posición...)"

    texto_cortina_rampa_render = FUENTE_TEXTO.render(texto_cortina_rampa_str, True, COLOR_TEXTO)
    PANTALLA.blit(texto_cortina_rampa_render, (10, 70))

    CORTINA_COLOR = (100, 100, 120)
    cortina_max_h = muelle_obj.get_rect().height - 10
    cortina_h = cortina_max_h
    cortina_y = muelle_obj.get_rect().top + 5

    if sistema_acoplamiento.estado_acoplamiento == "ABRIENDO_CORTINA":
        progreso_apertura = sistema_acoplamiento.tiempo_espera_actual / 2.0
        cortina_h = max(0, cortina_max_h * (1 - progreso_apertura))
        cortina_y = (muelle_obj.get_rect().top + 5) + (cortina_max_h - cortina_h)
    elif sistema_acoplamiento.motor_cortina.estado or \
         sistema_acoplamiento.estado_acoplamiento in ["LEVANTANDO_RAMPA", "BAJANDO_RAMPA", "ACOPLADO"]:
        cortina_h = 0

    if cortina_h > 0:
        cortina_rect_obj = pygame.Rect(muelle_obj.get_rect().left + 5, cortina_y, muelle_obj.get_rect().width - 10, cortina_h)
        pygame.draw.rect(PANTALLA, CORTINA_COLOR, cortina_rect_obj)

    RAMPA_COLOR = (120, 120, 100)
    rampa_h_max = 40
    rampa_h = 0
    rampa_x = muelle_obj.get_rect().left + 10
    rampa_y = muelle_obj.get_rect().centery - 10

    rampa_rect_obj = None
    if sistema_acoplamiento.estado_acoplamiento == "LEVANTANDO_RAMPA":
        progreso_levante = sistema_acoplamiento.tiempo_espera_actual / 2.0
        rampa_h = min(rampa_h_max, rampa_h_max * progreso_levante)
        rampa_rect_obj = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect_obj)
    elif sistema_acoplamiento.estado_acoplamiento == "BAJANDO_RAMPA":
        rampa_h = rampa_h_max
        rampa_rect_obj = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect_obj)
    elif sistema_acoplamiento.estado_acoplamiento == "ACOPLADO":
        rampa_h = rampa_h_max
        rampa_rect_obj = pygame.Rect(rampa_x - rampa_h, rampa_y, rampa_h, 20)
        pygame.draw.rect(PANTALLA, RAMPA_COLOR, rampa_rect_obj)

    pygame.display.flip()
    RELOJ.tick(FPS)

pygame.quit()
