"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# Mecanismos de sincronización
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)

def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))
        
        # 1. Esperar a que el tarro esté disponible (si el oso está comiendo o está lleno)
        sem_tarro_disponible.acquire()
        
        if not simulacion_activa:
            sem_tarro_disponible.release()
            break

        # 2. Entrar en exclusión mutua para modificar el tarro
        mutex.acquire()
        try:
            if tarro_miel < M and simulacion_activa:
                tarro_miel += 1
                print(f"🐝 Abeja {id_abeja} depositó miel. Tarro: {tarro_miel}/{M}")
                
                # 4. Si tarro_miel == M, despertar al oso
                if tarro_miel == M:
                    print(f"🍯 [Abeja {id_abeja}] ¡Tarro lleno! Despertando al oso 🐻")
                    sem_oso.release()
                    # No liberamos sem_tarro_disponible aquí; el oso lo liberará al vaciar el tarro
                else:
                    # 5. Si no está lleno, permitimos que otra abeja acceda
                    sem_tarro_disponible.release()
        finally:
            mutex.release()

def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros and simulacion_activa:
        # 1. Esperar pasivamente hasta que una abeja señale que el tarro está lleno
        sem_oso.acquire()
        
        if not simulacion_activa:
            break

        # 2. Comerse toda la miel
        mutex.acquire()
        print(f"🐻 [Oso] ¡Comiendo la miel! Tarro estaba con {tarro_miel} porciones.")
        tarro_miel = 0
        tarros_comidos += 1
        print(f"🐻 [Oso] Terminé de comer. Tarros comidos: {tarros_comidos}/{max_tarros}")
        mutex.release()

        # 4. Avisar a las abejas que el tarro está vacío y disponible
        sem_tarro_disponible.release()
        
        time.sleep(0.05)
        
    simulacion_activa = False
    # Liberar posibles bloqueos para que los hilos terminen limpiamente
    try:
        sem_tarro_disponible.release()
    except:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)
    
    # Crear hilo del oso
    hilo_oso = threading.Thread(target=oso, args=(2,))
    
    # Crear hilos de las abejas
    hilos_abejas = [threading.Thread(target=abeja, args=(i+1,)) for i in range(NUM_ABEJAS)]
    
    # Iniciar hilos
    hilo_oso.start()
    for h in hilos_abejas:
        h.start()
        
    # Esperar a que finalice el oso
    hilo_oso.join()
    
    # Asegurar cierre de abejas
    simulacion_activa = False
    for h in hilos_abejas:
        h.join()
        
    print("=" * 60)
    print(" Simulación del Oso y las Abejas finalizada con éxito.")
    print("=" * 60)