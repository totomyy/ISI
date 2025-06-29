import time
from Clases import *
from SistemaAcoplamiento import *

# Ejecución simulada
if input("¿Comenzar?\n") == "si":
    camion = Camion("C-101", distancia_inicial=5, alineado_izq=True, alineado_der=True)
    sistema = SistemaAcoplamiento()
    sistema.sensor_izq.set_valor(True)
    sistema.sensor_der.set_valor(True)
    sistema.sensor_distancia.set_valor(camion.distancia)
    sistema.acoplar_camion(camion)
