#!/usr/bin/env python3
"""
Sistema de Riego Inteligente Automatizado
==========================================

Sistema de control de riego para 3 canteros usando Raspberry Pi 4.
Controla electrovalvulas 12V mediante modulo de reles de 4 canales.
Registra automaticamente el consumo de agua en formato CSV.
"""

import csv
import os
import time
from datetime import datetime
try:
    import urllib.request
    import json
except ImportError:
    print("WARNING: urllib no disponible. Notificaciones deshabilitadas.")


# ============================================================================
# CONFIGURACION GLOBAL
# ============================================================================

# Modo de operacion: True para simulacion (sin hardware), False para GPIO real
MODO_SIMULACION = True

# URL del webhook de Make.com para notificaciones por email
# IMPORTANTE: Reemplazar con tu URL de Make.com
WEBHOOK_MAKE_URL = "https://hook.eu1.make.com/ku3rb5okwoyogpyxeqw7rfouojivkgih"

# Habilitar/deshabilitar notificaciones por email
NOTIFICACIONES_HABILITADAS = True

# Configuracion de canteros (GPIO y caudal)
CANTEROS = {
    1: {"nombre": "Cantero 1", "gpio": 17, "caudal_ml_min": 180},
    2: {"nombre": "Cantero 2", "gpio": 27, "caudal_ml_min": 180},
    3: {"nombre": "Cantero 3", "gpio": 22, "caudal_ml_min": 180},
}

# Archivo de log CSV
ARCHIVO_LOG = "riego_log.csv"

# Encabezados del CSV
CSV_HEADERS = ["fecha_hora", "cantero", "duracion_min", "volumen_ml", "estado"]


# ============================================================================
# MOCK GPIO - Simulador de GPIO para desarrollo sin hardware
# ============================================================================

class MockGPIO:
    """
    Simulador de GPIO compatible con RPi.GPIO API.
    Permite desarrollo y testing sin hardware real.
    """

    # Constantes compatibles con RPi.GPIO
    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.mode = None
        self.pins = {}
        self.warnings = True

    def setmode(self, mode):
        """Establece modo de numeracion de pines"""
        self.mode = mode
        if MODO_SIMULACION:
            print(f"[SIMULACION] GPIO mode establecido: {mode}")

    def setup(self, pin, mode):
        """Configura un pin como entrada o salida"""
        self.pins[pin] = {"mode": mode, "state": self.LOW}
        if MODO_SIMULACION:
            print(f"[SIMULACION] GPIO {pin} configurado como {mode}")

    def output(self, pin, state):
        """Establece estado de un pin de salida"""
        if pin in self.pins:
            self.pins[pin]["state"] = state
            estado_str = "activado" if state == self.HIGH else "desactivado"
            if MODO_SIMULACION:
                print(f"[SIMULACION] GPIO {pin} {estado_str}")
        else:
            raise RuntimeError(f"Pin {pin} no configurado")

    def cleanup(self):
        """Limpia configuracion de GPIO"""
        self.pins = {}
        if MODO_SIMULACION:
            print("[SIMULACION] GPIO cleanup completado")

    def setwarnings(self, flag):
        """Habilita/deshabilita warnings"""
        self.warnings = flag


# ============================================================================
# DATA LOGGER - Gestor de registros CSV
# ============================================================================

class DataLogger:
    """
    Gestor de logs de riego en formato CSV.
    Maneja creacion, escritura y lectura del archivo de registros.
    """

    def __init__(self, archivo=ARCHIVO_LOG):
        self.archivo = archivo
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        """Crea archivo CSV con encabezados si no existe"""
        if not os.path.exists(self.archivo):
            with open(self.archivo, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
            print(f"Archivo de log creado: {self.archivo}")

    def registrar_riego(self, cantero_num, duracion_min, volumen_ml, estado="completado"):
        """
        Registra un evento de riego en el CSV.

        Args:
            cantero_num (int): Numero de cantero (1-3)
            duracion_min (float): Duracion del riego en minutos
            volumen_ml (int): Volumen de agua aplicado en mililitros
            estado (str): Estado del riego (completado/error)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cantero_nombre = CANTEROS[cantero_num]["nombre"]

        registro = {
            "fecha_hora": timestamp,
            "cantero": cantero_nombre,
            "duracion_min": round(duracion_min, 2),
            "volumen_ml": volumen_ml,
            "estado": estado
        }

        with open(self.archivo, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(registro)

        return registro

    def obtener_historial(self, limite=10):
        """
        Obtiene ultimos registros del historial.

        Args:
            limite (int): Cantidad maxima de registros a retornar

        Returns:
            list: Lista de diccionarios con registros
        """
        registros = []

        if not os.path.exists(self.archivo):
            return registros

        with open(self.archivo, 'r', newline='') as f:
            reader = csv.DictReader(f)
            registros = list(reader)

        # Retornar ultimos N registros
        return registros[-limite:] if len(registros) > limite else registros

    def obtener_estadisticas(self):
        """
        Calcula estadisticas de riego por cantero.

        Returns:
            dict: Estadisticas por cantero
        """
        estadisticas = {}

        if not os.path.exists(self.archivo):
            return estadisticas

        with open(self.archivo, 'r', newline='') as f:
            reader = csv.DictReader(f)
            registros = list(reader)

        # Inicializar estadisticas para cada cantero
        for num, config in CANTEROS.items():
            nombre = config["nombre"]
            estadisticas[nombre] = {
                "total_riegos": 0,
                "volumen_total_ml": 0,
                "duracion_total_min": 0,
                "ultimo_riego": None
            }

        # Calcular estadisticas
        for reg in registros:
            cantero = reg["cantero"]
            if cantero in estadisticas:
                estadisticas[cantero]["total_riegos"] += 1
                estadisticas[cantero]["volumen_total_ml"] += int(reg["volumen_ml"])
                estadisticas[cantero]["duracion_total_min"] += float(reg["duracion_min"])
                estadisticas[cantero]["ultimo_riego"] = reg["fecha_hora"]

        # Calcular promedios
        for cantero in estadisticas:
            total_riegos = estadisticas[cantero]["total_riegos"]
            if total_riegos > 0:
                duracion_total = estadisticas[cantero]["duracion_total_min"]
                estadisticas[cantero]["duracion_promedio_min"] = round(
                    duracion_total / total_riegos, 2
                )
            else:
                estadisticas[cantero]["duracion_promedio_min"] = 0

        return estadisticas


# ============================================================================
# NOTIFICACIONES - Sistema de notificaciones por email via Make.com
# ============================================================================

def enviar_notificacion_email(cantero, duracion_min, volumen_ml, fecha_hora, estado="completado"):
    """
    Envia notificacion por email via Make.com cuando termina un riego.

    Args:
        cantero (str): Nombre del cantero regado
        duracion_min (float): Duracion del riego en minutos
        volumen_ml (int): Volumen de agua aplicado en mililitros
        fecha_hora (str): Timestamp del riego
        estado (str): Estado del riego (completado/error)
    """
    if not NOTIFICACIONES_HABILITADAS:
        return

    if WEBHOOK_MAKE_URL == "TU_URL_DE_MAKE_AQUI":
        print("[INFO] Notificaciones deshabilitadas: configura WEBHOOK_MAKE_URL")
        return

    try:
        # Preparar datos para enviar
        datos = {
            "cantero": cantero,
            "duracion_min": round(duracion_min, 2),
            "volumen_ml": volumen_ml,
            "volumen_litros": round(volumen_ml / 1000, 2),
            "fecha_hora": fecha_hora,
            "estado": estado
        }

        # Convertir a JSON
        datos_json = json.dumps(datos).encode('utf-8')

        # Crear request HTTP POST
        req = urllib.request.Request(
            WEBHOOK_MAKE_URL,
            data=datos_json,
            headers={'Content-Type': 'application/json'}
        )

        # Enviar request
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"[NOTIFICACION] Email enviado correctamente para {cantero}")
            else:
                print(f"[NOTIFICACION] Error al enviar email: HTTP {response.status}")

    except Exception as e:
        print(f"[NOTIFICACION] Error al enviar notificacion: {e}")


# ============================================================================
# IRRIGATION CONTROLLER - Controlador principal de riego
# ============================================================================

class IrrigationController:
    """
    Controlador principal del sistema de riego.
    Gestiona electrovalvulas, calcula volumenes y coordina operaciones.
    """

    def __init__(self, usar_gpio_real=False):
        """
        Inicializa el controlador.

        Args:
            usar_gpio_real (bool): True para usar GPIO real, False para simulacion
        """
        self.usar_gpio_real = usar_gpio_real
        self.logger = DataLogger()

        # Inicializar GPIO (real o simulado)
        if usar_gpio_real:
            try:
                import RPi.GPIO as GPIO
                self.gpio = GPIO
                print("Usando GPIO real de Raspberry Pi")
            except ImportError:
                print("ERROR: RPi.GPIO no disponible. Usando modo simulacion.")
                self.gpio = MockGPIO()
                self.usar_gpio_real = False
        else:
            self.gpio = MockGPIO()
            print("Modo SIMULACION activado")

        # Configurar GPIO
        self._configurar_gpio()

    def _configurar_gpio(self):
        """Configura pines GPIO para control de reles"""
        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)

        # Configurar cada pin como salida
        for cantero_num, config in CANTEROS.items():
            pin = config["gpio"]
            self.gpio.setup(pin, self.gpio.OUT)
            # Asegurar que empiecen apagados (reles desactivados)
            self.gpio.output(pin, self.gpio.LOW)

        print("GPIO configurado correctamente")

    def _calcular_volumen(self, cantero_num, duracion_min):
        """
        Calcula volumen de agua aplicado.

        Args:
            cantero_num (int): Numero de cantero
            duracion_min (float): Duracion en minutos

        Returns:
            int: Volumen en mililitros
        """
        caudal = CANTEROS[cantero_num]["caudal_ml_min"]
        volumen_ml = int(duracion_min * caudal)
        return volumen_ml

    def regar_cantero(self, cantero_num, duracion_min):
        """
        Ejecuta riego en un cantero especifico.

        Args:
            cantero_num (int): Numero de cantero (1-3)
            duracion_min (float): Duracion del riego en minutos

        Returns:
            dict: Informacion del riego realizado
        """
        if cantero_num not in CANTEROS:
            raise ValueError(f"Cantero {cantero_num} no valido. Use 1, 2 o 3.")

        if duracion_min <= 0:
            raise ValueError("Duracion debe ser mayor a 0")

        cantero = CANTEROS[cantero_num]
        nombre = cantero["nombre"]
        pin = cantero["gpio"]

        print(f"\n[SIMULACION] Iniciando riego en {nombre}..." if MODO_SIMULACION
              else f"\nIniciando riego en {nombre}...")

        try:
            # Activar electrovalvula (rele ON)
            self.gpio.output(pin, self.gpio.HIGH)

            # Simular riego (en produccion, aqui fluye el agua)
            print(f"Regando durante {duracion_min} minutos...")

            # Convertir minutos a segundos para time.sleep
            # En simulacion, aceleramos el tiempo (1 min = 1 seg)
            if MODO_SIMULACION:
                time.sleep(duracion_min)  # 1 minuto simulado = 1 segundo real
            else:
                time.sleep(duracion_min * 60)  # Tiempo real en produccion

            # Desactivar electrovalvula (rele OFF)
            self.gpio.output(pin, self.gpio.LOW)

            # Calcular volumen aplicado
            volumen_ml = self._calcular_volumen(cantero_num, duracion_min)

            # Registrar en log
            self.logger.registrar_riego(cantero_num, duracion_min, volumen_ml)

            print(f"Riego completado: {volumen_ml} ml aplicados")

            # Enviar notificacion por email
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            enviar_notificacion_email(nombre, duracion_min, volumen_ml, timestamp, "completado")

            return {
                "cantero": nombre,
                "duracion_min": duracion_min,
                "volumen_ml": volumen_ml,
                "estado": "completado"
            }

        except Exception as e:
            # En caso de error, asegurar que la valvula se cierre
            self.gpio.output(pin, self.gpio.LOW)
            print(f"ERROR durante riego: {e}")

            # Registrar error en log
            self.logger.registrar_riego(
                cantero_num, duracion_min, 0, estado="error"
            )

            # Enviar notificacion de error por email
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            enviar_notificacion_email(nombre, duracion_min, 0, timestamp, f"error: {str(e)}")

            return {
                "cantero": nombre,
                "duracion_min": duracion_min,
                "volumen_ml": 0,
                "estado": "error",
                "mensaje": str(e)
            }

    def riego_automatico(self, duracion_min_por_cantero):
        """
        Ejecuta riego automatico en todos los canteros secuencialmente.

        Args:
            duracion_min_por_cantero (float): Duracion para cada cantero

        Returns:
            list: Lista de resultados de cada riego
        """
        print("\n" + "="*50)
        print("INICIANDO RIEGO AUTOMATICO")
        print("="*50)

        resultados = []
        volumen_total = 0

        for cantero_num in sorted(CANTEROS.keys()):
            print(f"\n[{cantero_num}/{len(CANTEROS)}] Regando {CANTEROS[cantero_num]['nombre']}...")

            resultado = self.regar_cantero(cantero_num, duracion_min_por_cantero)
            resultados.append(resultado)
            volumen_total += resultado["volumen_ml"]

            # Pausa entre riegos (excepto en el ultimo)
            if cantero_num < max(CANTEROS.keys()):
                print("Esperando antes del siguiente cantero...")
                time.sleep(2 if MODO_SIMULACION else 10)

        print("\n" + "="*50)
        print("RIEGO AUTOMATICO COMPLETADO")
        print(f"Total aplicado: {volumen_total} ml ({volumen_total/1000:.2f} L)")
        print("="*50)

        return resultados

    def apagar_todo(self):
        """Apaga todas las electrovalvulas (seguridad)"""
        print("\nApagando todas las electrovalvulas...")
        for cantero_num, config in CANTEROS.items():
            pin = config["gpio"]
            self.gpio.output(pin, self.gpio.LOW)
        print("Todas las electrovalvulas apagadas")

    def cleanup(self):
        """Limpia recursos GPIO al finalizar"""
        self.apagar_todo()
        self.gpio.cleanup()
        print("Sistema detenido correctamente")


# ============================================================================
# INTERFAZ DE USUARIO - Menu interactivo
# ============================================================================

def mostrar_menu():
    """Muestra menu principal"""
    print("\n" + "="*50)
    print("   SISTEMA DE RIEGO INTELIGENTE")
    print("="*50)
    print(f"[MODO: {'SIMULACION' if MODO_SIMULACION else 'HARDWARE REAL'}]")
    print("\n1. Riego manual (un cantero)")
    print("2. Riego automatico (todos los canteros)")
    print("3. Ver historial de riego")
    print("4. Ver estadisticas")
    print("5. Salir")
    print("="*50)


def riego_manual(controller):
    """Interfaz para riego manual de un cantero"""
    print("\n" + "="*50)
    print("   RIEGO MANUAL")
    print("="*50)

    # Mostrar canteros disponibles
    print("\nCanteros disponibles:")
    for num, config in CANTEROS.items():
        print(f"  {num}. {config['nombre']} (GPIO {config['gpio']}) - {config['caudal_ml_min']} ml/min")

    # Solicitar cantero
    try:
        cantero = int(input("\nSeleccione cantero (1-3): "))
        if cantero not in CANTEROS:
            print("ERROR: Cantero no valido")
            return
    except ValueError:
        print("ERROR: Ingrese un numero valido")
        return

    # Solicitar duracion
    try:
        duracion = float(input("Duracion en minutos: "))
        if duracion <= 0:
            print("ERROR: Duracion debe ser mayor a 0")
            return
    except ValueError:
        print("ERROR: Ingrese un numero valido")
        return

    # Ejecutar riego
    controller.regar_cantero(cantero, duracion)


def riego_automatico(controller):
    """Interfaz para riego automatico de todos los canteros"""
    print("\n" + "="*50)
    print("   RIEGO AUTOMATICO")
    print("="*50)

    # Solicitar duracion
    try:
        duracion = float(input("\nDuracion por cantero (minutos): "))
        if duracion <= 0:
            print("ERROR: Duracion debe ser mayor a 0")
            return
    except ValueError:
        print("ERROR: Ingrese un numero valido")
        return

    # Ejecutar riego automatico
    controller.riego_automatico(duracion)


def ver_historial(controller):
    """Muestra historial de riegos"""
    print("\n" + "="*50)
    print("   HISTORIAL DE RIEGO")
    print("="*50)

    registros = controller.logger.obtener_historial(limite=10)

    if not registros:
        print("\nNo hay registros de riego todavia")
        return

    print(f"\nUltimos {len(registros)} riegos:")
    print("-" * 80)
    print(f"{'Fecha/Hora':<20} {'Cantero':<12} {'Duracion':<12} {'Volumen':<12} {'Estado':<10}")
    print("-" * 80)

    for reg in registros:
        fecha = reg["fecha_hora"]
        cantero = reg["cantero"]
        duracion = f"{reg['duracion_min']} min"
        volumen = f"{reg['volumen_ml']} ml"
        estado = reg["estado"]

        print(f"{fecha:<20} {cantero:<12} {duracion:<12} {volumen:<12} {estado:<10}")

    print("-" * 80)


def ver_estadisticas(controller):
    """Muestra estadisticas de riego por cantero"""
    print("\n" + "="*50)
    print("   ESTADISTICAS DE RIEGO")
    print("="*50)

    stats = controller.logger.obtener_estadisticas()

    if not stats:
        print("\nNo hay datos de riego todavia")
        return

    for cantero, datos in stats.items():
        print(f"\n{cantero}:")
        print(f"  Total de riegos: {datos['total_riegos']}")
        print(f"  Volumen total: {datos['volumen_total_ml']} ml ({datos['volumen_total_ml']/1000:.2f} L)")
        print(f"  Duracion promedio: {datos['duracion_promedio_min']} min")
        print(f"  Ultimo riego: {datos['ultimo_riego'] or 'Nunca'}")


def main():
    """Funcion principal del programa"""
    print("\n" + "="*60)
    print("  Sistema de Riego Inteligente - v1.0")
    print("  Autor: Agustin Diez | Python 3.7+")
    print("="*60)

    # Inicializar controlador
    controller = IrrigationController(usar_gpio_real=not MODO_SIMULACION)

    try:
        while True:
            mostrar_menu()

            try:
                opcion = input("\nSeleccione opcion: ").strip()

                if opcion == "1":
                    riego_manual(controller)

                elif opcion == "2":
                    riego_automatico(controller)

                elif opcion == "3":
                    ver_historial(controller)

                elif opcion == "4":
                    ver_estadisticas(controller)

                elif opcion == "5":
                    print("\nCerrando sistema...")
                    break

                else:
                    print("\nOpcion no valida. Intente nuevamente.")

            except KeyboardInterrupt:
                print("\n\nInterrupcion detectada. Cerrando sistema...")
                break

            except Exception as e:
                print(f"\nERROR: {e}")
                print("Intente nuevamente o contacte al administrador")

    finally:
        # Limpieza final
        controller.cleanup()
        print("\nSistema detenido. Hasta luego!\n")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
