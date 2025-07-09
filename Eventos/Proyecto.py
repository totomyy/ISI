import time
import datetime 
from clases import *
from sistemaAcoplamiento import *

if __name__ == "__main__":
    if input("¿Comenzar simulación? (si/no)\n").lower() == "si": 
        
        sistema_principal = SistemaAcoplamiento(distancia_activacion=1, tolerancia_distancia=0.5, tiempo_maximo_espera=5)
        sistema_principal.registrar_evento("--- INICIO DE SIMULACIONES ---", "SISTEMA")

        print("\n--- Simulación 1: Camión normal, acoplamiento y desacoplamiento ---")
        sistema_principal.registrar_evento("Inicio Simulación 1: Camión normal", "SIM")
        camion_normal = Camion("C-101", distancia_inicial=1.0, tamano=25, alineado_izq=True, alineado_der=True, desnivel_cm=2)
        if sistema_principal.acoplar_camion(camion_normal):
            sistema_principal.registrar_evento("Camión acoplado, iniciando desacoplamiento...", "SIM", camion_normal.id)
            time.sleep(2) 
            sistema_principal.secuencia_cierre(camion_normal)
        else:
            sistema_principal.registrar_evento("Fallo en acoplamiento, no se procede a desacoplar.", "SIM", camion_normal.id)
        sistema_principal.registrar_evento("Fin Simulación 1", "SIM")


        print(f"\n--- Simulación 2: Objeto Pequeño (tamaño < {SistemaAcoplamiento.UMBRAL_TAMANO_MINIMO_OBJETO}) ---")
        sistema_principal.registrar_evento("Inicio Simulación 2: Objeto Pequeño", "SIM")
        objeto_pequeno = Camion("Obj-002", distancia_inicial=1.0, tamano=5, alineado_izq=True, alineado_der=True) 
        sistema_principal.acoplar_camion(objeto_pequeno) 
        sistema_principal.registrar_evento("Fin Simulación 2", "SIM")


        print("\n--- Simulación 3: Camión Desalineado ---")
        sistema_principal.registrar_evento("Inicio Simulación 3: Camión Desalineado", "SIM")
        camion_desalineado = Camion("C-103", distancia_inicial=1.0, tamano=30, alineado_izq=False, alineado_der=True)
        sistema_principal.acoplar_camion(camion_desalineado) 
        sistema_principal.registrar_evento("Fin Simulación 3", "SIM")

        
        
        print("\n--- Simulación 4: Camión Tarda Demasiado (empieza lejos) ---")
        sistema_espera_corta = SistemaAcoplamiento(distancia_activacion=1, tiempo_maximo_espera=3)
        sistema_espera_corta.registrar_evento("Inicio Simulación 4: Camión Tarda Demasiado", "SIM")
        camion_lento = Camion("C-104", distancia_inicial=10, tamano=25, alineado_izq=True, alineado_der=True)
        sistema_espera_corta.acoplar_camion(camion_lento)
        sistema_espera_corta.registrar_evento("Fin Simulación 4", "SIM")


        print("\n--- Simulación 5: Camión se acerca progresivamente (usa sistema_principal) ---")
        sistema_principal.registrar_evento("Inicio Simulación 5: Camión se acerca progresivamente", "SIM")
        camion_progresivo = Camion("C-105", distancia_inicial=3.0, tamano=25, alineado_izq=True, alineado_der=True, desnivel_cm=1)
        if sistema_principal.acoplar_camion(camion_progresivo):
            sistema_principal.registrar_evento("Acoplado con éxito. Procediendo a desacoplar.", "SIM", camion_progresivo.id)
            time.sleep(1)
            sistema_principal.secuencia_cierre(camion_progresivo)
        sistema_principal.registrar_evento("Fin Simulación 5", "SIM")


        print("\n--- Simulación 6: Camión con Desnivel Excesivo ---")
        sistema_principal.registrar_evento("Inicio Simulación 6: Camión con Desnivel Excesivo", "SIM")
        camion_desnivel_alto = Camion("C-106", distancia_inicial=0.5, tamano=25, alineado_izq=True, alineado_der=True, desnivel_cm=10)
        
        if sistema_principal.acoplar_camion(camion_desnivel_alto):
            sistema_principal.registrar_evento("Acoplado (con alerta de desnivel). Procediendo a desacoplar.", "SIM", camion_desnivel_alto.id)
            time.sleep(1)
            sistema_principal.secuencia_cierre(camion_desnivel_alto)
        sistema_principal.registrar_evento("Fin Simulación 6", "SIM")

        print("\n--- Simulación 7: Camión con Desnivel Aceptable ---")
        sistema_principal.registrar_evento("Inicio Simulación 7: Camión con Desnivel Aceptable", "SIM")
        camion_desnivel_ok = Camion("C-107", distancia_inicial=0.5, tamano=25, alineado_izq=True, alineado_der=True, desnivel_cm=-4) 
        if sistema_principal.acoplar_camion(camion_desnivel_ok):
            sistema_principal.registrar_evento("Acoplado con desnivel aceptable. Procediendo a desacoplar.", "SIM", camion_desnivel_ok.id)
            time.sleep(1)
            sistema_principal.secuencia_cierre(camion_desnivel_ok)
        sistema_principal.registrar_evento("Fin Simulación 7", "SIM")
        
        sistema_principal.registrar_evento("--- FIN DE TODAS LAS SIMULACIONES ---", "SISTEMA")
        print(f"\nTodas las simulaciones completadas. Revisar el archivo '{SistemaAcoplamiento.NOMBRE_ARCHIVO_LOG}' para el registro detallado de eventos.")

    else:
        print("Simulación no iniciada.")
        
        with open(SistemaAcoplamiento.NOMBRE_ARCHIVO_LOG, "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} [SISTEMA] Simulación no iniciada por el usuario.\n")