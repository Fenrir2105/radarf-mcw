# Sistema FMCW Radar I/Q - Procesamiento Modular

Sistema de procesamiento en tiempo real para radar FMCW (Frequency Modulated Continuous Wave) con demodulación I/Q. Implementa detección de distancia, velocidad y dirección de objetos mediante análisis espectral de señales complejas.

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Funcionamiento Técnico](#funcionamiento-técnico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Visualización](#visualización)
- [Troubleshooting](#troubleshooting)

---

## Características

- **Procesamiento I/Q complejo**: Combina canales en cuadratura para detectar dirección
- **Adquisición dual asíncrona**: Lee simultáneamente dos puertos seriales (COM3/COM5)
- **Detección de parámetros físicos**:
  - Distancia al objeto (metros)
  - Velocidad relativa (m/s)
  - Dirección de movimiento (acercándose/alejándose/estático)
- **Visualización en tiempo real**: Gráficas de señales temporales, diagramas I/Q y espectros FFT
- **Arquitectura modular**: Componentes independientes y reutilizables

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     HARDWARE LAYER                          │
├──────────────────┬──────────────────────────────────────────┤
│   Serial COM3    │         Serial COM5                      │
│   (Canal I)      │         (Canal Q)                        │
└────────┬─────────┴──────────┬───────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│              SerialChannelReader (Threads)                  │
│  - Lectura asíncrona de paquetes                           │
│  - Parsing de protocolo (0xAA55 ... 0x55AA)               │
│  - Separación Up-chirp / Down-chirp                        │
└────────┬─────────────────────┬──────────────────────────────┘
         │                     │
         ▼                     ▼
    Queue_I               Queue_Q
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌──────────────────────┐
         │   RadarProcessor     │
         │  - Combina I+jQ      │
         │  - FFT compleja      │
         │  - Calcula R, v, dir │
         └──────────┬───────────┘
                    ▼
              Queue_Results
                    ▼
         ┌──────────────────────┐
         │    RadarPlotter      │
         │  - Visualización     │
         │  - Matplotlib        │
         └──────────────────────┘
```

### Componentes Principales

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| **Config** | `config/radar_config.py` | Parámetros centralizados del radar |
| **Data Models** | `core/data_models.py` | Estructuras de datos (ChannelData, RadarResults) |
| **Signal Processing** | `core/signal_processing.py` | Algoritmos FFT y cálculos físicos |
| **Packet Parser** | `hardware/packet_parser.py` | Decodificación del protocolo serial |
| **Serial Reader** | `hardware/serial_reader.py` | Lectura asíncrona de puertos COM |
| **Radar Processor** | `processing/radar_processor.py` | Procesamiento I/Q y detección |
| **Plotter** | `visualization/plotter.py` | Gráficas en tiempo real |
| **Main** | `main.py` | Orquestador del sistema |

---

## Requisitos

### Hardware
- Radar FMCW con salida I/Q separada
- 2 puertos seriales USB (COM3 y COM5 por defecto)
- Sistema operativo: Windows

### Software
```
Python >= 3.8
numpy >= 1.20.0
matplotlib >= 3.3.0
pyserial >= 3.5
```

---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/radar-fmcw-iq.git
cd radar-fmcw-iq
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
numpy==1.24.3
matplotlib==3.7.1
pyserial==3.5
```

---

## Configuración

Edita `config/radar_config.py` para ajustar parámetros:

```python
@dataclass
class RadarConfig:
    # Parámetros del radar
    Fs: float = 20000           # Hz - Frecuencia de muestreo
    N: int = 128                # Muestras por rampa
    B: float = 200e6            # Hz - Ancho de banda (200 MHz)
    c: float = 3e8              # m/s - Velocidad de la luz
    
    # Puertos seriales (AJUSTAR SEGÚN TU SISTEMA)
    port_I: str = "COM3"        # Canal I
    port_Q: str = "COM5"        # Canal Q
    baudrate: int = 115200
    timeout: float = 2.0
    
    # Procesamiento
    N_SAMPLES: int = 200        # Muestras por paquete serial
    velocity_threshold: float = 0.01  # m/s (umbral estático)
```

### Identificar puertos seriales

**Windows:**
```bash
# PowerShell
Get-WmiObject Win32_SerialPort | Select-Object Name,DeviceID
```

**Linux/Mac:**
```bash
ls /dev/tty.*       # Mac
ls /dev/ttyUSB*     # Linux
```

---

## Uso

### Ejecución básica
```bash
python main.py
```

### Salida esperada
```
======================================================================
           SISTEMA FMCW RADAR I/Q MODULAR
======================================================================
[I] Lector iniciado en COM3
[Q] Lector iniciado en COM5
[PROC] Procesador iniciado
[MAIN] Sistema iniciado
[VIS] Iniciando visualización

[I] Rampa SUBIDA recibida
[Q] Rampa SUBIDA recibida
[I] Rampa BAJADA recibida
[Q] Rampa BAJADA recibida
[I] Datos enviados a procesamiento
[Q] Datos enviados a procesamiento
[PROC] Datos I recibidos
[PROC] Datos Q recibidos
[PROC] Procesando señal compleja I+jQ...

======================================================================
              RESULTADOS RADAR FMCW (I/Q)
======================================================================
Frecuencia Up-chirp   (f_up)   =     1234.56 Hz
Frecuencia Down-chirp (f_down) =      987.65 Hz

             DISTANCIA              =     1.6650 m
             VELOCIDAD              =     0.1850 m/s
             DIRECCIÓN              = ACERCÁNDOSE 
======================================================================
```

### Detener el sistema
Presiona `Ctrl+C` en la terminal.

---

## Funcionamiento Técnico

### Principio FMCW

El radar FMCW transmite una señal cuya frecuencia varía linealmente (chirp). La señal reflejada se mezcla con la señal transmitida, produciendo una frecuencia de batido proporcional a:
- **Distancia**: Retardo temporal
- **Velocidad**: Efecto Doppler

### Demodulación I/Q

La señal mezclada se divide en dos canales ortogonales:
- **Canal I (In-phase)**: cos(φ)
- **Canal Q (Quadrature)**: sin(φ)

**Ventaja clave**: La señal compleja `S = I + jQ` preserva información de signo de frecuencia, permitiendo distinguir dirección de movimiento.

### Procesamiento de Señales

#### 1. Construcción de señal compleja
```python
signal_up = I_up + j*Q_up
signal_down = I_down + j*Q_down
```

#### 2. Análisis espectral (FFT)
```python
# Remover DC
signal = signal - mean(signal)

# Ventana de Hanning
windowed = signal * hanning(len(signal))

# FFT compleja (detecta frecuencias ±)
spectrum = fft(windowed)
spectrum = fftshift(spectrum)

# Detectar pico
f_peak = freqs[argmax(abs(spectrum))]
```

#### 3. Cálculo de parámetros físicos

**Distancia:**
```
R = (f_up + f_down) * c / (4*K)

donde K = B/T (tasa de cambio de frecuencia)
```

**Velocidad:**
```
v = (f_down - f_up)* c / (4 * f)
```

**Sentido:**
```
f_down > f_up  → objeto acercándose
f_down < f_up  → objeto alejándose
```

### Protocolo Serial

Cada paquete sigue la estructura:

```
┌────────┬────────┬────────┬────────────────────────────┬────────┬────────┐
│ 0xAA   │ 0x55   │ TYPE   │ DATA (N_SAMPLES * 2 bytes) │ 0x55   │ 0xAA   │
└────────┴────────┴────────┴────────────────────────────┴────────┴────────┘
   Byte0    Byte1    Byte2           Bytes 3..(3+2N-1)     ByteEnd-2 ByteEnd-1
▲                 ▲        ▲                            ▲
Header            Tipo     200 muestras                 Footer
                  1=Up    (2 bytes c/u)
                  2=Down
```

**Tipos de paquete:**
- `TYPE=1`: Rampa ascendente (Up-chirp) - primeras 128 muestras
- `TYPE=2`: Rampa descendente (Down-chirp) - últimas 128 muestras

---

## Estructura del Proyecto

```
radar_system/
│
├── main.py                      # Punto de entrada
│
├── config/
│   └── radar_config.py          # Parámetros del radar
│
├── core/
│   ├── data_models.py           # ChannelData, RadarResults
│   └── signal_processing.py    # SignalProcessor (FFT, cálculos)
│
├── hardware/
│   ├── packet_parser.py         # PacketParser (protocolo serial)
│   └── serial_reader.py         # SerialChannelReader (threads)
│
├── processing/
│   └── radar_processor.py       # RadarProcessor (combina I/Q)
│
├── visualization/
│   └── plotter.py               # RadarPlotter (matplotlib)
│
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## Visualización

El sistema genera una ventana con 6 gráficas:

```
┌──────────────────────────────────┬─────────────────┐
│   Señal I/Q Completa (temporal)  │                 │
│   [Up-chirp | Down-chirp]        │   Panel de      │
├─────────────────┬────────────────┤   Resultados    │
│  Diagrama I/Q   │  Diagrama I/Q  │   - Frecuencias │
│   (Up-chirp)    │  (Down-chirp)  │   - Distancia   │
├─────────────────┼────────────────┤   - Velocidad   │
│   FFT Compleja  │  FFT Compleja  │   - Dirección   │
│   (Up-chirp)    │  (Down-chirp)  │                 │
└─────────────────┴────────────────┴─────────────────┘
```

### Interpretación

1. **Señal temporal**: Amplitudes I/Q concatenadas con transición marcada
2. **Diagrama I/Q**: Trayectoria en plano complejo (detecta rotación)
3. **FFT**: Espectro con pico de frecuencia marcado
4. **Panel**: Resumen con código de colores
   - 🟢 Verde: Estático
   - 🔴 Rojo: Acercándose
   - 🔵 Cyan: Alejándose

---

## Troubleshooting

### Error: "No se pudo abrir COM3"

**Causa**: Puerto ocupado o no existe

**Solución**:
```bash
# Verificar puertos disponibles
# Windows: Device Manager → Ports (COM & LPT)
# Linux: ls /dev/ttyUSB*

# Ajustar en config/radar_config.py
port_I: str = "COM4"  # Cambiar según tu sistema
```

### Error: "Queue llena"

**Causa**: Procesamiento más lento que adquisición

**Solución**:
```python
# En config/radar_config.py
queue_size: int = 10  # Aumentar de 5 a 10
```

### No se visualizan gráficas

**Causa**: Backend de matplotlib no interactivo

**Solución**:
```bash
# Instalar backend TkInter
sudo apt-get install python3-tk  # Linux
# o usar otro backend en visualization/plotter.py:
import matplotlib
matplotlib.use('TkAgg')
```

### Frecuencias detectadas = 0 Hz

**Causa**: Señal sin objeto o ruido puro

**Verificar**:
1. Conexiones de hardware (antenas, cables)
2. Alimentación del radar
3. Objeto dentro del rango de detección

### Valores erráticos de distancia/velocidad

**Causa**: Desincronización entre canales I/Q

**Solución**:
- Verificar trigger común en hardware
- Reducir `timeout` en configuración
- Revisar integridad de paquetes seriales

---


## Licencia

MIT License - Ver archivo `LICENSE` para detalles

---

**Última actualización**: Noviembre 2025