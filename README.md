# Sistema de Riego Inteligente Automatizado
## Trabajo Práctico - Automatización de Complejidad Media

---

## 📋 Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Justificación y Alcance](#justificación-y-alcance)
3. [Modo Simulación (Sin Hardware)](#modo-simulación-sin-hardware)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Implementación Realizada](#implementación-realizada)
6. [Estructura del Código](#estructura-del-código)
7. [Ejecución y Pruebas](#ejecución-y-pruebas)
8. [Datos Generados (CSV)](#datos-generados-csv)
9. [Funcionalidades Pendientes](#funcionalidades-pendientes)
10. [Guía de Instalación y Puesta en Marcha](#guía-de-instalación-y-puesta-en-marcha)
11. [Visualización Rápida de la Arquitectura de Conexión](#visualización-rápida-de-la-arquitectura-de-conexión)

---

## Descripción del Proyecto

**Sistema de riego inteligente automatizado para tres canteros** implementado con **Python puro** (sin librerías externas) y preparado para **Raspberry Pi 4**.

La solución controla 3 electroválvulas 12V mediante un módulo de relés de 4 canales, registra automáticamente el consumo de agua por cantero y genera logs verificables en formato CSV.

### Características Principales

✅ **Control automático y manual** de 3 canteros independientes
✅ **Medición precisa** de volumen de agua aplicado (ml)
✅ **Registro detallado** de cada riego en archivo CSV
✅ **Modo simulación completa** (sin hardware) para corrección
✅ **Mock de GPIO y relés** compatible con API real
✅ **Caudal parametrizable** por cantero
✅ **Medición por tiempo** con cálculo automático de volumen
✅ **Sin dependencias externas** (solo biblioteca estándar de Python)
✅ **Migración directa** a GPIO real cuando se disponga de hardware

### Contexto Real

Este sistema está diseñado para automatizar el riego en casa del autor, donde se tienen:
- **3 canteros de cemento** montados sobre estructura metálica escalonada
- **Conexión directa** a canilla principal con derivación a 4 líneas
- **Caudal estable** de aproximadamente 180 ml/min por línea
- **Hardware preparado:** Raspberry Pi 4, módulo relé 4 canales, electroválvulas 12V NC

---

## Justificación y Alcance

### ¿Por qué este proyecto cumple los requisitos del TP?

**1. Complejidad Media**
- Integración de múltiples componentes (GPIO, relés, electroválvulas)
- Lógica de control con estados y temporización
- Gestión de datos persistentes (CSV)
- Interfaz de usuario interactiva

**2. Automatización Real**
- Aplicación práctica inmediata en entorno doméstico
- Soluciona problema real: riego manual ineficiente
- Sistema end-to-end verificable

**3. Generación de Datos Propios**
- Logs CSV con timestamp, zona, duración, volumen
- Estadísticas calculadas en tiempo real
- Trazabilidad completa de operaciones

**4. Robustez y Trazabilidad**
- Manejo de errores y estados
- Logs persistentes para auditoría
- Modo seguro (apagado automático de electroválvulas)

**5. Desarrollo con IA (Pair Programming)**
- Todo el código generado en diálogo con Claude
- Sin uso de librerías externas (requisito del TP)
- Sin orquestadores (puro Python)

---

## Modo Simulación (Sin Hardware)

### 🎯 Enfoque del TP: Corregible sin Hardware

El proyecto está **completamente funcional en modo simulación**, permitiendo su ejecución, prueba y corrección **sin necesidad de tener la Raspberry Pi ni el hardware hidráulico conectado**.

### ¿Cómo funciona la simulación?

#### 1. **Mock de GPIO (Pines I/O)**

Se implementó una clase `MockGPIO` que simula completamente el comportamiento de la biblioteca `RPi.GPIO`:

```python
class MockGPIO:
    """Simulador de GPIO compatible con RPi.GPIO API"""
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def setup(self, pin, mode):
        """Configura un pin como entrada/salida"""
        print(f"[SIMULACIÓN] GPIO {pin} configurado como {mode}")

    def output(self, pin, state):
        """Activa/desactiva un pin"""
        estado = "activado" if state == HIGH else "desactivado"
        print(f"[SIMULACIÓN] GPIO {pin} {estado}")
```

**Ventajas:**
- API idéntica a `RPi.GPIO` real
- Mensajes informativos de cada operación
- Fácil migración a hardware real (cambiar 1 línea de código)

#### 2. **Mock de Relés**

Los relés se simulan mediante el control de pines GPIO virtuales:
- Cuando `GPIO.output(pin, HIGH)` → **Relé activado** → Electroválvula abierta (simulada)
- Cuando `GPIO.output(pin, LOW)` → **Relé desactivado** → Electroválvula cerrada (simulada)

#### 3. **Caudal Parametrizable por Cantero**

Cada cantero tiene su caudal configurado en el diccionario `CANTEROS`:

```python
CANTEROS = {
    1: {"nombre": "Cantero 1", "gpio": 17, "caudal_ml_min": 180},
    2: {"nombre": "Cantero 2", "gpio": 27, "caudal_ml_min": 180},
    3: {"nombre": "Cantero 3", "gpio": 22, "caudal_ml_min": 180},
}
```

**Parametrización fácil:** Cambiar el valor `caudal_ml_min` para ajustar cada cantero.

#### 4. **Medición por Tiempo**

El sistema mide el tiempo que la electroválvula permanece abierta y calcula el volumen:

```python
volumen_ml = duracion_minutos × caudal_ml_min
```

**Ejemplo:**
- Cantero 1: 5 minutos × 180 ml/min = **900 ml**
- Cantero 2: 3.5 minutos × 180 ml/min = **630 ml**

#### 5. **Aceleración del Tiempo en Simulación**

Para facilitar las pruebas:
- **Modo simulación:** 1 minuto de riego = **1 segundo real**
- **Modo hardware:** 1 minuto de riego = **60 segundos reales**

```python
if MODO_SIMULACION:
    time.sleep(duracion_min)  # Acelerado
else:
    time.sleep(duracion_min * 60)  # Tiempo real
```

### 📊 Verificación de la Simulación

Al ejecutar el sistema en modo simulación, se pueden observar:

1. **Mensajes de GPIO simulado:**
   ```
   [SIMULACIÓN] GPIO 17 configurado como OUT
   [SIMULACIÓN] GPIO 17 activado
   [SIMULACIÓN] GPIO 17 desactivado
   ```

2. **Cálculos de volumen correctos:**
   ```
   Riego completado: 900 ml aplicados
   ```

3. **Registros CSV generados:**
   ```csv
   2025-01-15 08:30:00,Cantero 1,5.0,900,completado
   ```

4. **Estadísticas calculadas:**
   ```
   Cantero 1: 12 riegos, 10800 ml (10.8 L)
   ```

## Arquitectura del Sistema

### Flujo de Datos

```
┌─────────────────┐
│  Python Script  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GPIO Pins      │ (17, 27, 22)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Módulo Relé    │ (4 canales, 5V)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Electroválvulas │ (12V NC)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Canteros     │ (3 zonas)
└─────────────────┘
```

### Proceso de Riego

1. Python ejecuta riego programado o manual
2. Activa GPIO correspondiente de la Raspberry Pi
3. GPIO acciona el relé asignado
4. Relé abre la electroválvula (12V)
5. Agua fluye hacia el cantero seleccionado
6. Python mide tiempo activo
7. Calcula mililitros aplicados (ml = minutos × caudal)
8. Guarda resultado en log CSV verificable

---

## Especificaciones Técnicas

### Hardware de Control

| Componente | Modelo/Especificación |
|------------|----------------------|
| Controlador | Raspberry Pi 4 |
| Módulo Relé | 4 canales, 5V, opto-aislado |
| Electroválvulas | 12V DC, NC (Normalmente Cerradas) |
| Fuente Electroválvulas | 12V DC, mínimo 2A |
| Fuente Raspberry | 5V DC, 3A (oficial) |

### Configuración GPIO

| Pin GPIO | Relé | Cantero | Ubicación |
|----------|------|---------|-----------|
| GPIO 17  | Relé 1 | Cantero 1 | Izquierda |
| GPIO 27  | Relé 2 | Cantero 2 | Centro |
| GPIO 22  | Relé 3 | Cantero 3 | Derecha |
| GND      | GND | - | Tierra común |
| 5V       | VCC | - | Alimentación relé |

### Parámetros Hidráulicos

| Cantero | Caudal (ml/min) | Capacidad Estimada |
|---------|----------------|-------------------|
| Cantero 1 | 180 | Variable según sustrato |
| Cantero 2 | 180 | Variable según sustrato |
| Cantero 3 | 180 | Variable según sustrato |

**Presión de trabajo:** Conexión directa a canilla principal
**Tipo de distribución:** 1 entrada → 4 salidas (3 activas + 1 reserva)

---

## Hardware Hidráulico

### Componentes Necesarios

- **3 Electroválvulas 12V NC** (normalmente cerradas)
- **Distribuidor/manifold** 1 entrada → 3-4 salidas
- **Manguera flexible** para derivación a cada cantero
- **Abrazaderas y conectores** hidráulicos
- **Válvula de paso manual** (opcional, corte general)
- **Cinta teflón** para roscas

### Consumibles Eléctricos

- Cable eléctrico calibre 18-20 AWG
- Cables dupont hembra-hembra y macho-hembra
- Terminales y conectores eléctricos
- Protoboard o borneras de conexión
- Tornillos de montaje

---

## Estructura de Datos

### Formato del Log CSV

```csv
fecha_hora,cantero,duracion_min,volumen_ml,estado
2025-01-15 08:30:00,Cantero 1,5.0,900,completado
2025-01-15 08:35:30,Cantero 2,3.5,630,completado
2025-01-15 18:00:00,Cantero 3,4.0,720,completado
```

**Campos:**
- `fecha_hora`: Timestamp en formato YYYY-MM-DD HH:MM:SS
- `cantero`: Identificador del cantero (Cantero 1, 2 o 3)
- `duracion_min`: Tiempo de riego en minutos (float)
- `volumen_ml`: Agua aplicada en mililitros (calculado)
- `estado`: Estado del riego (completado/error)

---

## Instalación y Configuración

### Requisitos del Sistema

- **Sistema Operativo:** Raspberry Pi OS (Bullseye o superior)
- **Python:** 3.7+ (incluido en Raspberry Pi OS)
- **Librerías:** Solo biblioteca estándar de Python (sin dependencias externas)

### Instalación Rápida

1. **Clonar o copiar el proyecto:**
```bash
mkdir ~/AutoriegoPY
cd ~/AutoriegoPY
# Copiar sistema_riego.py al directorio
```

2. **Verificar Python:**
```bash
python3 --version  # Debe ser 3.7 o superior
```

3. **Ejecutar en modo simulación:**
```bash
python3 sistema_riego.py
```

### Migración a Hardware Real

Para usar con hardware GPIO real de Raspberry Pi:

1. Instalar biblioteca GPIO (solo para hardware real):
```bash
pip3 install RPi.GPIO
```

2. Editar `sistema_riego.py`:
```python
# Cambiar en la línea correspondiente:
MODO_SIMULACION = False  # Cambiar a False para usar GPIO real
```

3. Ejecutar con permisos de GPIO:
```bash
sudo python3 sistema_riego.py
```

---

## Uso del Sistema

### Menú Principal

Al ejecutar el programa, aparece el menú interactivo:

```
=== SISTEMA DE RIEGO INTELIGENTE ===
[MODO: SIMULACIÓN]

1. Riego manual (un cantero)
2. Riego automático (todos los canteros)
3. Ver historial de riego
4. Ver estadísticas
5. Salir

Seleccione opción:
```

### Opciones del Menú

#### 1. Riego Manual
- Permite seleccionar un cantero específico (1, 2 o 3)
- Ingresar duración en minutos
- Calcula y muestra volumen de agua aplicado
- Registra el riego en el log

#### 2. Riego Automático
- Riega todos los canteros en secuencia
- Duración configurable (misma para todos)
- Espera entre riegos para evitar sobrecarga
- Genera registro completo

#### 3. Ver Historial
- Muestra los últimos 10 riegos registrados
- Información completa: fecha, cantero, duración, volumen
- Formato tabular legible

#### 4. Ver Estadísticas
- Total de riegos por cantero
- Volumen total aplicado por cantero
- Duración promedio de riego
- Última fecha de riego por cantero

#### 5. Salir
- Cierra el programa de forma segura
- Asegura que todos los relés estén apagados

---

## Ejemplos de Uso

### Ejemplo 1: Riego Manual de un Cantero

```
Seleccione opción: 1

=== RIEGO MANUAL ===
Canteros disponibles:
  1. Cantero 1 (GPIO 17) - 180 ml/min
  2. Cantero 2 (GPIO 27) - 180 ml/min
  3. Cantero 3 (GPIO 22) - 180 ml/min

Seleccione cantero (1-3): 1
Duración en minutos: 5

[SIMULACIÓN] Iniciando riego en Cantero 1...
[SIMULACIÓN] GPIO 17 activado
Regando durante 5.0 minutos...
[SIMULACIÓN] GPIO 17 desactivado
Riego completado: 900 ml aplicados
```

### Ejemplo 2: Riego Automático de Todos los Canteros

```
Seleccione opción: 2

=== RIEGO AUTOMÁTICO ===
Duración por cantero (minutos): 3

Iniciando secuencia de riego automático...

[1/3] Regando Cantero 1...
[SIMULACIÓN] GPIO 17 activado
Regando durante 3.0 minutos...
[SIMULACIÓN] GPIO 17 desactivado
Completado: 540 ml

[2/3] Regando Cantero 2...
[SIMULACIÓN] GPIO 27 activado
Regando durante 3.0 minutos...
[SIMULACIÓN] GPIO 27 desactivado
Completado: 540 ml

[3/3] Regando Cantero 3...
[SIMULACIÓN] GPIO 22 activado
Regando durante 3.0 minutos...
[SIMULACIÓN] GPIO 22 desactivado
Completado: 540 ml

Riego automático completado.
Total aplicado: 1620 ml
```

### Ejemplo 3: Ver Estadísticas

```
Seleccione opción: 4

=== ESTADÍSTICAS DE RIEGO ===

Cantero 1:
  Total de riegos: 12
  Volumen total: 10800 ml (10.8 L)
  Duración promedio: 5.0 min
  Último riego: 2025-01-15 08:30:00

Cantero 2:
  Total de riegos: 10
  Volumen total: 7200 ml (7.2 L)
  Duración promedio: 4.0 min
  Último riego: 2025-01-15 08:35:30

Cantero 3:
  Total de riegos: 11
  Volumen total: 9540 ml (9.54 L)
  Duración promedio: 4.8 min
  Último riego: 2025-01-15 18:00:00
```

---

## Implementación Realizada

### ✅ Componentes Implementados

#### 1. **Mock de GPIO (MockGPIO)**
```python
class MockGPIO:
    - Simula API completa de RPi.GPIO
    - Métodos: setmode(), setup(), output(), cleanup()
    - Compatible con código de producción
    - Mensajes informativos para debugging
```

**Estado:** ✅ Completamente funcional

#### 2. **Gestor de Datos (DataLogger)**
```python
class DataLogger:
    - Creación automática de archivo CSV
    - Registro de riegos con timestamp
    - Lectura de historial (últimos N registros)
    - Cálculo de estadísticas por cantero
```

**Estado:** ✅ Completamente funcional

#### 3. **Controlador de Riego (IrrigationController)**
```python
class IrrigationController:
    - Inicialización de GPIO (real o mock)
    - Riego manual (un cantero, duración variable)
    - Riego automático (todos los canteros)
    - Cálculo automático de volumen
    - Seguridad: apagado de electroválvulas
```

**Estado:** ✅ Completamente funcional

#### 4. **Interfaz de Usuario (main)**
```python
def main():
    - Menú interactivo de 5 opciones
    - Riego manual y automático
    - Visualización de historial
    - Visualización de estadísticas
    - Manejo de errores y excepciones
```

**Estado:** ✅ Completamente funcional

### 📊 Funcionalidades Operativas

| Funcionalidad | Estado | Descripción |
|--------------|--------|-------------|
| Riego manual | ✅ | Riego de un cantero específico con duración personalizada |
| Riego automático | ✅ | Riego secuencial de todos los canteros |
| Registro CSV | ✅ | Log automático de cada riego con timestamp |
| Historial | ✅ | Consulta de últimos 10 riegos |
| Estadísticas | ✅ | Total riegos, volumen total, promedio por cantero |
| Cálculo de volumen | ✅ | ml = minutos × caudal_ml_min |
| Mock GPIO | ✅ | Simulación completa sin hardware |
| Apagado seguro | ✅ | Cierre automático de electroválvulas al salir |
| Manejo de errores | ✅ | Try-except en operaciones críticas |

---

## Estructura del Código

### Arquitectura de `sistema_riego.py`

```
sistema_riego.py (18 KB, ~450 líneas)
│
├── [CONFIGURACIÓN GLOBAL]
│   ├── MODO_SIMULACION = True
│   ├── CANTEROS = {1, 2, 3} con GPIO y caudal
│   ├── ARCHIVO_LOG = "riego_log.csv"
│   └── CSV_HEADERS = [fecha_hora, cantero, ...]
│
├── [CLASE MockGPIO]
│   ├── __init__()
│   ├── setmode(mode)
│   ├── setup(pin, mode)
│   ├── output(pin, state)
│   ├── cleanup()
│   └── setwarnings(flag)
│
├── [CLASE DataLogger]
│   ├── __init__(archivo)
│   ├── _inicializar_archivo()
│   ├── registrar_riego(cantero, duracion, volumen, estado)
│   ├── obtener_historial(limite)
│   └── obtener_estadisticas()
│
├── [CLASE IrrigationController]
│   ├── __init__(usar_gpio_real)
│   ├── _configurar_gpio()
│   ├── _calcular_volumen(cantero, duracion)
│   ├── regar_cantero(cantero, duracion)
│   ├── riego_automatico(duracion_por_cantero)
│   ├── apagar_todo()
│   └── cleanup()
│
├── [INTERFAZ DE USUARIO]
│   ├── mostrar_menu()
│   ├── riego_manual(controller)
│   ├── riego_automatico(controller)
│   ├── ver_historial(controller)
│   ├── ver_estadisticas(controller)
│   └── main()
│
└── [PUNTO DE ENTRADA]
    └── if __name__ == "__main__": main()
```

### Dependencias del Proyecto

**Librerías utilizadas (solo estándar de Python):**
```python
import csv        # Gestión de archivos CSV
import os         # Operaciones de sistema de archivos
import time       # Control de temporización
from datetime import datetime  # Timestamps
```

**NO se utilizan:**
- ❌ RPi.GPIO (se usa mock en simulación)
- ❌ Ninguna librería externa
- ❌ Frameworks o orquestadores

### Detalles de Implementación

#### Configuración de Canteros (Parametrizable)

```python
CANTEROS = {
    1: {
        "nombre": "Cantero 1",
        "gpio": 17,
        "caudal_ml_min": 180  # ← Parametrizable
    },
    2: {
        "nombre": "Cantero 2",
        "gpio": 27,
        "caudal_ml_min": 180  # ← Parametrizable
    },
    3: {
        "nombre": "Cantero 3",
        "gpio": 22,
        "caudal_ml_min": 180  # ← Parametrizable
    }
}
```

**Fácil personalización:** Modificar `caudal_ml_min` para ajustar según cada cantero.

#### Fórmula de Cálculo de Volumen

```python
def _calcular_volumen(self, cantero_num, duracion_min):
    caudal = CANTEROS[cantero_num]["caudal_ml_min"]
    volumen_ml = int(duracion_min * caudal)
    return volumen_ml
```

**Ejemplo de cálculos:**
- 2.0 min × 180 ml/min = **360 ml**
- 5.0 min × 180 ml/min = **900 ml**
- 10.0 min × 180 ml/min = **1800 ml** (1.8 L)

---

## Ejecución y Pruebas

### 🚀 Ejecución del Sistema

#### Paso 1: Verificar Python

```bash
python3 --version
# Debe mostrar: Python 3.7 o superior
```

#### Paso 2: Ejecutar el sistema

```bash
cd /Users/agustindiez/Documents/AutoriegoPY
python3 sistema_riego.py
```

#### Paso 3: Interactuar con el menú

```
==================================================
   SISTEMA DE RIEGO INTELIGENTE
==================================================
[MODO: SIMULACIÓN]

1. Riego manual (un cantero)
2. Riego automático (todos los canteros)
3. Ver historial de riego
4. Ver estadísticas
5. Salir
==================================================

Seleccione opción:
```

### 🧪 Casos de Prueba Recomendados

#### Test 1: Riego Manual de Cantero 1

```
Seleccione opción: 1
Seleccione cantero (1-3): 1
Duración en minutos: 2

Resultado esperado:
✅ [SIMULACIÓN] GPIO 17 activado
✅ Regando durante 2.0 minutos...
✅ [SIMULACIÓN] GPIO 17 desactivado
✅ Riego completado: 360 ml aplicados
```

#### Test 2: Riego Automático de Todos los Canteros

```
Seleccione opción: 2
Duración por cantero (minutos): 3

Resultado esperado:
✅ [1/3] Regando Cantero 1... → 540 ml
✅ [2/3] Regando Cantero 2... → 540 ml
✅ [3/3] Regando Cantero 3... → 540 ml
✅ Total aplicado: 1620 ml (1.62 L)
```

#### Test 3: Ver Historial

```
Seleccione opción: 3

Resultado esperado:
✅ Tabla con últimos riegos
✅ Columnas: Fecha/Hora, Cantero, Duración, Volumen, Estado
```

#### Test 4: Ver Estadísticas

```
Seleccione opción: 4

Resultado esperado:
✅ Cantero 1: Total riegos, volumen total, promedio
✅ Cantero 2: Total riegos, volumen total, promedio
✅ Cantero 3: Total riegos, volumen total, promedio
✅ Último riego de cada cantero
```

### 📝 Salida de Ejemplo (Riego Manual)

```
==================================================
   RIEGO MANUAL
==================================================

Canteros disponibles:
  1. Cantero 1 (GPIO 17) - 180 ml/min
  2. Cantero 2 (GPIO 27) - 180 ml/min
  3. Cantero 3 (GPIO 22) - 180 ml/min

Seleccione cantero (1-3): 1
Duración en minutos: 5

[SIMULACIÓN] Iniciando riego en Cantero 1...
[SIMULACIÓN] GPIO 17 activado
Regando durante 5.0 minutos...
[SIMULACIÓN] GPIO 17 desactivado
Riego completado: 900 ml aplicados
```

---

## Datos Generados (CSV)

### Formato del Archivo `riego_log.csv`

El sistema genera automáticamente un archivo CSV con la siguiente estructura:

```csv
fecha_hora,cantero,duracion_min,volumen_ml,estado
2025-01-15 08:30:00,Cantero 1,5.0,900,completado
2025-01-15 08:35:30,Cantero 2,3.5,630,completado
2025-01-15 09:00:00,Cantero 3,4.0,720,completado
2025-01-15 18:00:00,Cantero 1,2.0,360,completado
2025-01-15 18:05:00,Cantero 2,2.0,360,completado
2025-01-15 18:10:00,Cantero 3,2.0,360,completado
```

### Descripción de Campos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `fecha_hora` | string | Timestamp en formato YYYY-MM-DD HH:MM:SS | `2025-01-15 08:30:00` |
| `cantero` | string | Nombre del cantero regado | `Cantero 1` |
| `duracion_min` | float | Duración del riego en minutos | `5.0` |
| `volumen_ml` | int | Volumen de agua aplicado en mililitros | `900` |
| `estado` | string | Estado del riego (completado/error) | `completado` |

### Ejemplo de Análisis de Datos

Con el CSV generado, se pueden realizar análisis como:

**Total de agua aplicada por día:**
```python
# Filtrar registros por fecha
# Sumar volumen_ml de todos los riegos
# Convertir a litros (dividir por 1000)
```

**Frecuencia de riego por cantero:**
```python
# Contar registros agrupados por cantero
# Calcular promedio de días entre riegos
```

**Consumo promedio por riego:**
```python
# Calcular promedio de volumen_ml por cantero
# Identificar patrones de consumo
```

### 📊 Trazabilidad Completa

El archivo CSV proporciona:
✅ **Auditoría:** Historial completo de operaciones
✅ **Análisis:** Datos para optimizar frecuencia y duración
✅ **Verificación:** Comprobación de volúmenes aplicados
✅ **Debugging:** Identificación de riegos fallidos (estado=error)

---

## Funcionalidades Pendientes

### 🔄 Mejoras Futuras (No implementadas en esta versión)

#### Prioridad Alta
- [ ] **Programación por horarios** (estilo cron)
  - Riego automático a horario fijo (ej: 8:00 AM y 6:00 PM)
  - Calendario de riego por día de semana
  - Configuración persistente de horarios

- [ ] **Sensor de humedad de suelo**
  - Lectura de sensor capacitivo/resistivo
  - Riego condicional según humedad medida
  - Umbral configurable por cantero

#### Prioridad Media
- [ ] **Control remoto vía web**
  - Servidor web simple (HTTP)
  - Interfaz HTML para control desde móvil/PC
  - API REST para integración

- [ ] **Notificaciones**
  - Envío de email al finalizar riego automático
  - Alertas por Telegram
  - Notificación de errores

- [ ] **Ajuste automático según clima**
  - Integración con API de pronóstico del tiempo
  - Cancelación de riego si hay lluvia programada
  - Ajuste de duración según temperatura

#### Prioridad Baja
- [ ] **Interfaz gráfica (GUI)**
  - Ventana con botones para cada cantero
  - Gráficos de consumo histórico
  - Configuración visual de parámetros

- [ ] **Dashboard de visualización**
  - Gráficos de consumo por cantero
  - Tendencias semanales/mensuales
  - Exportación de reportes

- [ ] **Cuarto cantero**
  - Habilitar Relé 4 del módulo
  - Configurar GPIO 23 para Cantero 4
  - Actualizar menú y estadísticas

### 🛠️ Mejoras Técnicas Pendientes

- [ ] Validación exhaustiva de entrada de usuario
- [ ] Configuración de caudales desde archivo externo (JSON/config)
- [ ] Modo "dry-run" para previsualizar riegos programados
- [ ] Backup automático de archivo CSV
- [ ] Rotación de logs por tamaño/fecha
- [ ] Tests unitarios automatizados

## Guía de Instalación y Puesta en Marcha

### 🎯 Objetivo

Esta guía te lleva paso a paso desde cero hasta tener tu sistema de riego funcionando, explicado de forma simple y práctica.

---

## 📦 Paso 1: Lista de Materiales

### Hardware Electrónico

| Componente | Especificación | Precio Ref. (ARG 2025) |
|------------|----------------|------------------------|
| **Raspberry Pi 4** | 2GB RAM o superior + Kit (fuente, case, SD) | $80.000 - $120.000 |
| **MicroSD** | 16GB mínimo (32GB recomendado), Clase 10 | Incluido en kit |
| **Adaptador microSD → USB** | Para grabar desde tu PC | $2.000 - $3.000 |
| **Módulo Relé** | 4 canales, 5V, opto-aislado | $3.000 - $5.000 |
| **Cables Dupont** | Kit macho-hembra (40 cables) | $2.000 - $3.000 |

### Hardware Hidráulico

| Componente | Especificación | Precio Ref. (ARG 2025) |
|------------|----------------|------------------------|
| **Electroválvulas 12V NC** | 12V DC, rosca 1/2", normalmente cerradas (x3) | $8.000 - $15.000 c/u |
| **Fuente 12V** | 12V DC, mínimo 2A | $5.000 - $8.000 |
| **Manguera flexible** | 1/2", 10 metros | $4.000 - $6.000 |
| **Conectores y abrazaderas** | Varios | $3.000 - $5.000 |
| **Teflón** | Para roscas | $500 |

**💰 Total estimado: $100.000 - $150.000 ARS**

### Periféricos (Solo Configuración Inicial)

- Monitor + cable HDMI (prestado o temporal)
- Teclado USB (prestado o temporal)
- Mouse USB (opcional)

---

## 🔧 Paso 2: Preparar la Raspberry Pi

### 2.1 Instalar Raspberry Pi OS en la MicroSD

**Desde tu PC (Windows/Mac/Linux):**

1. **Insertar microSD** en adaptador USB → Conectar a tu PC

2. **Descargar Raspberry Pi Imager:**
   - Web oficial: https://www.raspberrypi.com/software/
   - Instalar en tu PC

3. **Grabar el sistema operativo:**
   - Abrir Raspberry Pi Imager
   - **Choose Device:** Raspberry Pi 4
   - **Choose OS:** Raspberry Pi OS (32-bit)
   - **Choose Storage:** Tu microSD

4. **Configuración avanzada** (click en ⚙️):
   ```
   ✅ Set hostname: raspberrypi
   ✅ Enable SSH: Sí (con contraseña)
   ✅ Set username: pi
   ✅ Set password: [tu contraseña]
   ✅ Configure WiFi:
      SSID: [tu red WiFi]
      Password: [contraseña WiFi]
      Country: AR
   ✅ Set locale:
      Timezone: America/Argentina/Buenos_Aires
      Keyboard: es
   ```

5. **Grabar:** Click en "NEXT" → "YES" → Esperar 10-20 minutos

6. **Expulsar de forma segura** la microSD de tu PC

### 2.2 Primer Arranque

1. **Insertar microSD** en la Raspberry Pi (ranura inferior, hasta "clic")
2. **Conectar:**
   - Cable HDMI → Monitor
   - Teclado USB
   - Cable Ethernet (opcional si configuraste WiFi)
   - **Por último:** Cable USB-C de corriente

3. **Arranque automático:**
   - LED rojo fijo (alimentación)
   - LED verde parpadeando (actividad)
   - Pantalla muestra arranque de Linux

4. **Configuración inicial:**
   - Si configuraste WiFi en Imager → arranca directo al escritorio
   - Si no → usar asistente de configuración

5. **Verificar conexión a Internet:**
   ```bash
   # Abrir terminal y probar:
   ping -c 4 google.com
   ```

---

## ⚡ Paso 3: Conexión del Hardware

### 3.1 Identificar Pines GPIO

**Esquema de pines Raspberry Pi (vista superior):**

```
     3.3V  [ 1] [ 2]  5V       ← Alimentación relé
    GPIO2  [ 3] [ 4]  5V
    GPIO3  [ 5] [ 6]  GND
    GPIO4  [ 7] [ 8]  GPIO14
      GND  [ 9] [10]  GPIO15   ← GND para relé
   GPIO17  [11] [12]  GPIO18   ← Cantero 1
   GPIO27  [13] [14]  GND      ← Cantero 2
   GPIO22  [15] [16]  GPIO23   ← Cantero 3
     3.3V  [17] [18]  GPIO24
   GPIO10  [19] [20]  GND
   ...
```

**Usaremos:**
- Pin 2 (5V) → VCC del relé
- Pin 9 (GND) → GND del relé
- Pin 11 (GPIO17) → IN1 del relé (Cantero 1)
- Pin 13 (GPIO27) → IN2 del relé (Cantero 2)
- Pin 15 (GPIO22) → IN3 del relé (Cantero 3)

### 3.2 Conectar Raspberry Pi → Módulo Relé

**⚠️ Raspberry Pi APAGADA (sin alimentación)**

| Raspberry Pi | Cable | Módulo Relé |
|--------------|-------|-------------|
| Pin 2 (5V) | Rojo | VCC |
| Pin 11 (GPIO17) | Amarillo | IN1 |
| Pin 13 (GPIO27) | Naranja | IN2 |
| Pin 15 (GPIO22) | Verde | IN3 |
| Pin 9 (GND) | Negro | GND |

**Diagrama de conexión:**

```
Raspberry Pi                    Módulo Relé 4 Canales
────────────                    ─────────────────────

Pin 2  [5V]  ──[Rojo]─────────→ VCC
Pin 11 [GPIO17] ──[Amarillo]──→ IN1 (Cantero 1)
Pin 13 [GPIO27] ──[Naranja]───→ IN2 (Cantero 2)
Pin 15 [GPIO22] ──[Verde]─────→ IN3 (Cantero 3)
Pin 9  [GND] ──[Negro]────────→ GND
```

### 3.3 Conectar Electroválvulas al Relé

**Cada electroválvula se conecta a su relé correspondiente:**

```
Fuente 12V              Relé 1               Electroválvula 1
──────────              ──────               ────────────────

+12V ─────────────────→ COM
                        NO ────────────────→ Cable Rojo (+)
GND ──────────────────────────────────────→ Cable Negro (-)

[Repetir para Relé 2/EV2 y Relé 3/EV3]
```

**Importante:**
- Usar pin **NO** (Normalmente Abierto), NO usar NC
- Todas las electroválvulas comparten el GND de la fuente 12V
- Ajustar bien los tornillos de los bornes del relé

---

## 💻 Paso 4: Instalación del Software

### 4.1 Actualizar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 Instalar Librería GPIO

```bash
sudo apt install python3-rpi.gpio -y
```

**Verificar:**
```bash
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
```

### 4.3 Copiar el Sistema de Riego

**Opción A: Clonar desde repositorio**
```bash
cd ~
git clone [URL_DEL_REPO] AutoriegoPY
cd AutoriegoPY
```

**Opción B: Copiar manualmente**
```bash
# Desde tu PC:
scp sistema_riego.py pi@raspberrypi.local:~/
```

### 4.4 Configurar Modo Hardware

Editar `sistema_riego.py`:

```bash
nano sistema_riego.py
```

**Cambiar esta línea:**
```python
MODO_SIMULACION = False  # Cambiar de True a False
```

Guardar: `Ctrl + O`, `Enter`, `Ctrl + X`

---

## 🧪 Paso 5: Pruebas del Sistema

### 5.1 Prueba Sin Agua (Solo Relés)

```bash
sudo python3 sistema_riego.py
```

**Verificar:**
- [ ] Los relés hacen "clic" al activarse
- [ ] Los LEDs del módulo relé se encienden/apagan
- [ ] No hay errores en pantalla

**Probar riego manual:**
```
Seleccione opción: 1
Cantero: 1
Duración: 0.1  # 6 segundos (0.1 min)
```

### 5.2 Prueba con Agua (Conexión Hidráulica)

1. **Conectar electroválvulas** a las mangueras de riego
2. **Conectar entrada de agua** al distribuidor
3. **Abrir llave de paso** lentamente
4. **Ejecutar riego corto:**
   ```
   Opción: 1
   Cantero: 1
   Duración: 0.5  # 30 segundos
   ```
5. **Verificar:**
   - [ ] Sale agua del cantero correcto
   - [ ] Se detiene correctamente
   - [ ] No hay fugas

---

## 🤖 Paso 6: Automatización (Opcional)

### Opción A: Riego Programado con Cron

**Editar crontab:**
```bash
crontab -e
```

**Ejemplos de programación:**
```bash
# Riego diario a las 8:00 AM (2 minutos por cantero)
0 8 * * * cd ~/AutoriegoPY && echo "2" | sudo python3 sistema_riego.py >> riego.log 2>&1

# Dos riegos diarios (8 AM y 8 PM)
0 8,20 * * * cd ~/AutoriegoPY && echo "2" | sudo python3 sistema_riego.py >> riego.log 2>&1
```

### Opción B: Servicio Systemd (Avanzado)

Crear servicio:
```bash
sudo nano /etc/systemd/system/riego.service
```

Contenido:
```ini
[Unit]
Description=Sistema de Riego Automático
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/AutoriegoPY
ExecStart=/usr/bin/python3 /home/pi/AutoriegoPY/sistema_riego.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable riego.service
sudo systemctl start riego.service
```

---

## 📊 Paso 7: Calibración de Caudales

**Para medición precisa de agua:**

1. **Regar 5 minutos** con un cantero
2. **Recolectar agua** en un recipiente medido
3. **Calcular caudal real:**
   ```
   Ejemplo: Si recolectaste 850 ml en 5 min
   Caudal = 850 / 5 = 170 ml/min
   ```
4. **Actualizar en código:**
   ```python
   CANTEROS = {
       1: {"nombre": "Cantero 1", "gpio": 17, "caudal_ml_min": 170},  # Ajustado
       2: {"nombre": "Cantero 2", "gpio": 27, "caudal_ml_min": 185},  # Ajustado
       3: {"nombre": "Cantero 3", "gpio": 22, "caudal_ml_min": 175},  # Ajustado
   }
   ```

---

## ❌ Solución de Problemas Comunes

### Raspberry Pi No Enciende

**Causas:**
- Fuente insuficiente (usar 5V 3A oficial)
- MicroSD mal insertada o corrupta
- Cable USB-C defectuoso

**Solución:**
1. Verificar LED rojo encendido
2. Probar con otra fuente
3. Reinstalar sistema en microSD

### Relé No Hace Clic

**Causas:**
- Cables GPIO mal conectados
- Sin permisos (falta `sudo`)
- Pin GPIO incorrecto

**Solución:**
```bash
# Probar manualmente:
sudo su
echo "17" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value  # Debe hacer clic
echo "0" > /sys/class/gpio/gpio17/value
echo "17" > /sys/class/gpio/unexport
exit
```

### Electroválvula No Abre (Relé Funciona)

**Causas:**
- Sin alimentación 12V
- Conectada a pin NC en vez de NO
- Electroválvula defectuosa

**Solución:**
1. Verificar 12V con multímetro
2. Cambiar cable de NC a NO
3. Probar electroválvula directo a 12V

### No Sale Agua

**Causas:**
- Llave de paso cerrada
- Sin presión de agua
- Filtro obstruido

**Solución:**
1. Verificar presión en canilla
2. Limpiar filtros
3. Revisar mangueras dobladas

---

## 🔒 Precauciones de Seguridad

### ⚠️ Seguridad Eléctrica

- ✅ Desconectar todo antes de hacer cambios
- ✅ Separar circuitos: 5V (Raspberry) / 12V (Electroválvulas) / 220V (Alimentación)
- ✅ Usar módulo relé **opto-aislado**
- ✅ No tocar cables con corriente
- ❌ NUNCA conectar 12V directo a GPIO

### ⚠️ Seguridad Hidráulica

- ✅ Instalar válvula de corte manual
- ✅ Probar en seco antes de conectar agua
- ✅ Usar abrazaderas en todas las uniones
- ✅ Verificar no haya pérdidas
- ✅ Primeras pruebas con tiempos cortos (10-30 seg)

---

## 🎯 Checklist Final

### Antes de Poner en Producción

- [ ] Raspberry Pi arranca correctamente
- [ ] Conectado a WiFi/Ethernet
- [ ] Software actualizado (`sudo apt update`)
- [ ] RPi.GPIO instalado
- [ ] Conexiones GPIO verificadas
- [ ] Relés hacen clic al activarse
- [ ] Electroválvulas abren/cierran
- [ ] Prueba con agua exitosa
- [ ] No hay fugas
- [ ] Caudales calibrados
- [ ] Logs CSV funcionando
- [ ] (Opcional) Cron configurado

---

## 📚 Recursos Adicionales

### Documentación

- Guía oficial Raspberry Pi GPIO: https://www.raspberrypi.com/documentation/
- Python CSV: https://docs.python.org/3/library/csv.html
- Cron: `man crontab`

### Soporte

- Revisar logs: `tail -f riego_log.csv`
- Ver estadísticas: Opción 4 del menú
- Backup de config: `cp sistema_riego.py sistema_riego_backup.py`

---

## 🎓 Resumen de Comandos Útiles

```bash
# Ejecutar sistema
sudo python3 sistema_riego.py

# Ver últimos riegos
tail -20 riego_log.csv

# Editar programación
crontab -e

# Reiniciar Raspberry
sudo reboot

# Apagar Raspberry de forma segura
sudo shutdown -h now

# Ver estado del servicio (si usas systemd)
sudo systemctl status riego.service

# Ver temperatura de la Raspberry
vcgencmd measure_temp
```

---

**⏱️ Tiempo total estimado de instalación: 3-4 horas**
**💡 Dificultad: Media (con paciencia, cualquiera puede hacerlo)**

---

## Visualización Rápida de la Arquitectura de Conexión

### 🎯 Guía Ultra-Simplificada: Del Humano al Agua

Esta es la explicación más simple posible de cómo funciona todo el sistema, paso a paso, con tus manos.

---

### 🧩 PASO 1 — Comprar o Tener los Elementos

**Con tus manos necesitás:**

- ✔ **Raspberry Pi** (cualquier modelo 3 o 4)
- ✔ **MicroSD** (16GB o más)
- ✔ **Adaptador microSD → USB** (para ponerla en tu PC)
- ✔ **Cargador USB-C** de Raspberry Pi
- ✔ **Cable HDMI**
- ✔ **Monitor y teclado** (solo para la primera vez)
- ✔ **Módulo relé** (4 canales, 5V)
- ✔ **Cables jumper** (macho-hembra, varios colores)
- ✔ **Electroválvula 12V** (normalmente cerrada)
- ✔ **Fuente 12V** (para la electroválvula)

---

### 🧩 PASO 2 — Preparar la microSD DESDE TU PC

**1. Poné la microSD dentro del adaptador**

Físicamente:
```
microSD → dentro del adaptador
adaptador → puerto USB de tu PC
```

**2. En tu PC bajá Raspberry Pi Imager**

De la web oficial:
```
https://www.raspberrypi.com/software/
```

**3. Abrí el programa Raspberry Pi Imager**

**4. Elegí:**
```
Choose OS → Raspberry Pi OS (32-bit)
Choose Storage → tu microSD
```

**5. Apretá WRITE**

Raspberry Pi Imager va a instalar Linux en la microSD.

⏱️ Esperá 10-20 minutos

**6. Cuando termine → SACÁS la microSD del adaptador**

⚠️ **Importante:** Expulsar de forma segura antes de sacar

---

### 🧩 PASO 3 — Insertar la microSD en la Raspberry Pi

**Físico:**

1. Agarrás la microSD con los dedos
2. La metés en la ranura de la Raspberry (abajo, chiquita)
3. Empujás despacito hasta que haga **"clic"**

```
    ┌─────────────┐
    │ Raspberry Pi│
    │             │
    └──────┬──────┘
        ▼
    ╔═══════╗
    ║microSD║ ← Insertada
    ╚═══════╝
```

---

### 🧩 PASO 4 — Conectar la Raspberry Pi y Arrancar Linux

**Físico:**

1. Conectá el **HDMI** de la Raspberry al monitor
2. Conectá un **teclado USB** a la Raspberry
3. Conectá el **cable USB-C** de corriente

**Resultado:**
- La Raspberry se enciende sola
- Linux aparece en pantalla
- **No tocás nada más:** inicia solo

```
Monitor ←[HDMI]← Raspberry Pi
                      ↑
                  [USB-C Power]
                      ↑
                   220V ⚡
```

---

### 🧩 PASO 5 — Configurar Linux por Primera Vez

**Con el teclado:**

1. Elegís **idioma:** Español
2. Elegís **WiFi** (nombre de tu red y contraseña)
3. Elegís **zona horaria:** Buenos Aires
4. Se reinicia

**Listo:** Linux está instalado y funcionando ✅

---

### 🧩 PASO 6 — Crear tu Archivo Python

**En Linux, escribís:**

1. Abrís la **terminal** (ícono negro arriba)

2. Escribís:
```bash
nano regar.py
```

3. En el archivo pegás:
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

GPIO.output(17, 1)
time.sleep(2)
GPIO.output(17, 0)

GPIO.cleanup()
```

4. Guardás con:
```
CTRL + O
ENTER
CTRL + X
```

**Listo:** Ya tenés tu script ✅

---

### 🧩 PASO 7 — Conectar el Relé al Pin GPIO17

**Físico:**

Con los cables jumper (de colores):

```
Raspberry Pi Pin 11 (GPIO17) →[Cable Amarillo]→ IN del relé
Raspberry Pi Pin 9  (GND)    →[Cable Negro]→ GND del relé
Raspberry Pi Pin 2  (5V)     →[Cable Rojo]→ VCC del relé
```

**Diagrama visual:**

```
Raspberry Pi                Módulo Relé
────────────                ───────────

Pin 2  [5V] ──Rojo────────→ VCC
Pin 11 [GPIO17] ──Amarillo→ IN
Pin 9  [GND] ──Negro──────→ GND
```

**Con tus manos:**
1. Agarrás un cable amarillo hembra
2. Lo enchufás en el pin 11 de la Raspberry
3. El otro extremo lo enchufás en "IN" del relé
4. Repetís con los cables rojo (5V→VCC) y negro (GND→GND)

---

### 🧩 PASO 8 — Conectar la Electroválvula al Relé

**Físico (lado de potencia):**

```
Fuente 12V (+) ────────────→ COM del relé
Relé (NO) ─────────────────→ Cable ROJO de la electroválvula
Fuente 12V (-) ────────────→ Cable NEGRO de la electroválvula
```

**Diagrama completo:**

```
┌──────────┐
│Fuente 12V│
│  + | -   │
└──┬───┬───┘
   │   │
   │   └──────────────────────┐
   │                          │
   │   ┌──────────────┐       │
   └──→│Relé          │       │
       │ COM  NO  NC  │       │
       └───────┬──────┘       │
               │              │
               ▼              ▼
       ┌──────────────────────┐
       │   Electroválvula     │
       │   ROJO(+)  NEGRO(-)  │
       └──────────────────────┘
```

**Con tus manos:**
1. Cable de +12V → borne COM del relé (ajustar con destornillador)
2. Cable de NO del relé → cable rojo de la electroválvula
3. Cable de GND 12V → cable negro de la electroválvula

---

### 🧩 PASO 9 — Ejecutar el Código

**En la terminal escribir:**

```bash
sudo python3 regar.py
```

---

### 🧩 PASO 10 — ¿Qué Pasa Físicamente?

**Cuando ejecutás el código, esto ocurre:**

```
1. Python ejecuta la línea:
   GPIO.output(17, 1)

2. Físicamente:
   El pin GPIO17 sube a 3.3V
   ↓
   Esa señal llega al relé por el cable amarillo
   ↓
   El relé hace "CLIC" (sonido mecánico)
   ↓
   El relé cierra el circuito de 12V
   ↓
   Los 12V llegan a la electroválvula
   ↓
   La electroválvula se ABRE
   ↓
   💧 CORRE AGUA

3. Después de 2 segundos:
   GPIO.output(17, 0)
   ↓
   GPIO17 baja a 0V
   ↓
   El relé hace "CLIC" otra vez
   ↓
   El relé abre el circuito de 12V
   ↓
   La electroválvula se CIERRA
   ↓
   ⛔ SE CORTA EL AGUA
```

---

### 📊 Flujo Completo: Del Código al Agua

```
┌─────────────────────────────────────────────────────────┐
│  TU CÓDIGO EN PYTHON                                    │
│  GPIO.output(17, 1)  →  Encender pin 17                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  RASPBERRY PI                                           │
│  Pin 11 (GPIO17) pasa de 0V → 3.3V                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (cable amarillo)
┌─────────────────────────────────────────────────────────┐
│  MÓDULO RELÉ                                            │
│  Recibe señal 3.3V → Activa bobina → Hace "CLIC"       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (cierra circuito de 12V)
┌─────────────────────────────────────────────────────────┐
│  ELECTROVÁLVULA                                         │
│  Recibe 12V → Abre el paso de agua                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  💧 AGUA FLUYE HACIA TUS PLANTAS                        │
└─────────────────────────────────────────────────────────┘
```

---

### 🎯 Resumen en 3 Capas

**Capa 1: SOFTWARE**
- Python controla los pines GPIO
- `GPIO.output(17, 1)` = encender
- `GPIO.output(17, 0)` = apagar

**Capa 2: ELECTRÓNICA**
- Raspberry Pi (3.3V) controla el relé
- Relé (switch) controla electroválvula (12V)
- Separación de circuitos para seguridad

**Capa 3: FÍSICA**
- Electroválvula abre/cierra paso de agua
- Agua va desde canilla → electroválvula → planta
- Todo automatizado sin intervención humana

---

### ✅ Verificación Paso a Paso

Para saber que funciona:

| Paso | ¿Qué verificar? | ✅ OK |
|------|----------------|-------|
| 1 | Raspberry enciende (LED rojo) | |
| 2 | Linux arranca en pantalla | |
| 3 | Terminal funciona | |
| 4 | Script no da errores | |
| 5 | Relé hace "CLIC" | |
| 6 | LED del relé enciende | |
| 7 | Electroválvula abre (se siente) | |
| 8 | Sale agua por la manguera | |

---

**💡 Esto es todo lo que necesitás entender para que funcione el sistema.**

El resto (logs, estadísticas, programación por horarios) son mejoras que se agregan sobre esta base.

---

## Instalación y Configuración

### Requisitos del Sistema

- **Sistema Operativo:**
  - Desarrollo: macOS, Linux, Windows
  - Producción: Raspberry Pi OS (Bullseye o superior)
- **Python:** 3.7+ (incluido en Raspberry Pi OS y macOS)
- **Librerías:** Solo biblioteca estándar de Python
- **Espacio:** <1 MB (código + logs)

### Instalación Rápida (Modo Simulación)

```bash
# 1. Navegar al directorio del proyecto
cd /Users/agustindiez/Documents/AutoriegoPY

# 2. Verificar Python
python3 --version  # Debe ser 3.7+

# 3. Ejecutar (no requiere instalación)
python3 sistema_riego.py
```

**¡Listo!** El sistema se ejecuta inmediatamente en modo simulación.

### Instalación en Raspberry Pi (Hardware Real)

```bash
# 1. Copiar archivos a la Raspberry Pi
scp sistema_riego.py pi@raspberrypi.local:~/

# 2. Conectarse a la Raspberry
ssh pi@raspberrypi.local

# 3. Instalar RPi.GPIO
pip3 install RPi.GPIO

# 4. Editar MODO_SIMULACION = False en el código

# 5. Ejecutar con permisos
sudo python3 sistema_riego.py
```

---

## Mantenimiento y Monitoreo

### Mantenimiento Recomendado

| Frecuencia | Tarea | Tiempo Estimado |
|------------|-------|----------------|
| **Semanal** | Verificar estado de mangueras y conexiones | 5 min |
| **Mensual** | Limpiar filtros de electroválvulas | 15 min |
| **Trimestral** | Revisar logs y calibrar caudales | 30 min |
| **Semestral** | Inspección completa de conexiones eléctricas | 1 hora |
| **Anual** | Reemplazo preventivo de mangueras | 2 horas |

### Monitoreo del Sistema

#### Revisar Logs Periódicamente

```bash
# Ver últimos riegos
tail -20 riego_log.csv

# Contar total de riegos
wc -l riego_log.csv

# Buscar errores
grep "error" riego_log.csv
```

#### Estadísticas desde el Sistema

Opción 4 del menú → "Ver estadísticas" proporciona:
- Total de riegos por cantero
- Volumen total aplicado (en litros)
- Duración promedio de riego
- Fecha del último riego

### Backup de Datos

**Recomendado:** Hacer backup del archivo CSV semanalmente:

```bash
# Backup manual
cp riego_log.csv riego_log_backup_$(date +%Y%m%d).csv

# Programar backup automático (crontab)
0 0 * * 0 cp ~/AutoriegoPY/riego_log.csv ~/backups/riego_log_$(date +\%Y\%m\%d).csv
```

---

## Créditos y Licencia

### Autor

**Agustín Diez**
- Proyecto: Sistema de Riego Inteligente Automatizado
- Fecha: Enero 2025
- Contexto: Trabajo Práctico - Automatización de Complejidad Media

### Tecnologías Utilizadas

- **Lenguaje:** Python 3.7+
- **Hardware (proyectado):** Raspberry Pi 4, Módulo Relé 4 canales, Electroválvulas 12V NC
- **Metodología:** Pair programming con IA (Claude de Anthropic)
- **Paradigma:** Código generado 100% mediante diálogo (sin librerías externas, sin orquestadores)

### Desarrollo

**Asistencia de IA:** Claude (Anthropic)
- Todo el código fue generado en sesión de pair programming
- Requisitos del TP: sin librerías externas, sin orquestadores
- Enfoque: modo simulado para corrección sin hardware

### Archivos del Proyecto

```
AutoriegoPY/
├── sistema_riego.py   (18 KB) - Sistema completo
├── README.md          (actual) - Documentación
└── riego_log.csv      (auto)  - Logs de riego
```

### Contacto

Para consultas, mejoras o reportar problemas con el sistema:
- **Repositorio local:** `/Users/agustindiez/Documents/AutoriegoPY`
- **Archivo principal:** `sistema_riego.py`

---

## Referencias y Recursos

### Documentación Técnica

- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.org/documentation/usage/gpio/)
- [Python CSV Module](https://docs.python.org/3/library/csv.html)
- [Python Time Module](https://docs.python.org/3/library/time.html)
- [Python Datetime Module](https://docs.python.org/3/library/datetime.html)

### Hardware

- [Relay Module Specifications](https://www.electronicwings.com/raspberry-pi/raspberry-pi-relay-module)
- Electroválvulas 12V NC: Especificaciones del fabricante
- Raspberry Pi 4: Pinout oficial

### Aprendizaje

- Automatización con Python: Conceptos básicos
- GPIO Programming: Control de hardware con software
- IoT en el hogar: Proyectos prácticos

---

## Resumen Ejecutivo para Presentación

### 📊 Datos del Proyecto

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | Sistema de Riego Inteligente Automatizado |
| **Tipo** | Automatización de complejidad media |
| **Lenguaje** | Python 3 (solo biblioteca estándar) |
| **Líneas de código** | ~450 líneas |
| **Archivos** | 1 archivo Python + 1 README + 1 CSV auto-generado |
| **Modo** | Simulación (sin hardware) + Migración directa a real |
| **Canteros** | 3 independientes (expandible a 4) |
| **Medición** | Por tiempo × caudal parametrizable |
| **Trazabilidad** | Log CSV completo con timestamp |

### ✅ Cumplimiento de Requisitos del TP

1. ✅ **Complejidad media** - Control GPIO + lógica + persistencia
2. ✅ **Automatización real** - Aplicable en casa del autor
3. ✅ **Generación de datos** - CSV con fecha, zona, minutos, ml
4. ✅ **Robustez** - Manejo de errores, apagado seguro
5. ✅ **Trazabilidad** - Historial completo auditable
6. ✅ **Sin librerías externas** - Solo Python estándar
7. ✅ **Sin orquestadores** - Todo en Python puro
8. ✅ **Pair programming con IA** - Código generado con Claude
9. ✅ **Modo simulado** - Corregible sin hardware
10. ✅ **Mock completo** - GPIO y relés simulados

### 🎯 Puntos Clave para la Exposición

1. **Problema real:** Riego manual ineficiente en 3 canteros en casa
2. **Solución completa:** Hardware + Software + Datos
3. **Totalmente verificable:** Funciona SIN hardware (modo simulación)
4. **Migración simple:** 1 línea de código para pasar a producción
5. **Datos propios:** CSV auto-generado con métricas reales
6. **Parametrizable:** Caudales ajustables por cantero
7. **Escalable:** Preparado para 4to cantero, sensores, web, etc.

---

**Versión:** 1.0
**Última actualización:** Noviembre 2025
**Estado:** ✅ Completamente funcional en modo simulación
