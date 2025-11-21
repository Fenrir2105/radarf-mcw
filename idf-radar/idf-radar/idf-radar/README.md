# ESP32 ADC Sampler – Proyecto ESP-IDF

### Adquisición Continua de Señales I/Q para Radar FMCW

Este módulo corresponde al firmware desarrollado en **ESP-IDF** para los ESP32 encargados de muestrear las señales I y Q provenientes del front-end del radar FMCW.

El ESP32 captura datos en modo **ADC continuo**, sincronizado por un trigger externo, y envía las muestras por UART al módulo Python de procesamiento.

---

## Características principales

* **Modo de captura:** Muestreo ADC en *continuous mode* (TYPE1).
* **Frecuencia de muestreo:** Configurable (Default: `20 kHz`).
* **Sincronización:** Lectura activada por trigger externo (`GPIO 26`).
* **Detección de flancos:**
    * Flanco de subida: Inicia captura de **Rampa Ascendente**.
    * Flanco de bajada: Inicia captura de **Rampa Descendente**.
* **Protocolo UART:** Envío de paquetes con estructura propia y cabeceras de seguridad.
    * Formato: `[0xAA 0x55 TYPE | DATA(n) | 0x55 0xAA]`
* **Compatibilidad:** Totalmente compatible con ESP-IDF 5.1+.
* **Modularidad:** Diseño configurable mediante `config.h`.

---

## Estructura del proyecto

```text
idf-radar/
│── main/
│   ├── main.c         # Lógica principal: ADC, triggers, UART
│   └── config.h       # Configuraciones generales del sistema
│
└── CMakeLists.txt
---
## Funcionamiento general
1. Inicialización
El sistema configura los periféricos en el siguiente orden:

Configuración del puerto UART.

Configuración del GPIO de trigger (Entrada).

Configuración del ADC continuo.

Creación del handle del ADC.

2. Bucle principal
El ESP32 entra en un ciclo infinito de espera y captura:

Espera flanco de subida → Inicia captura → Envía `TYPE_RISING_EDGE`.

Espera flanco de bajada → Inicia captura → Envía `TYPE_FALLING_EDGE`.

Cada grupo de captura contiene `N_SAMPLES` valores de 12 bits.
---

## Protocolo de comunicación
Los datos se envían al sistema de procesamiento en Python mediante un paquete binario estructurado:

Estructura del Paquete: 
```
[ CABECERA (3 bytes) | DATOS (N_SAMPLES * 2 bytes) | PIE (2 bytes) ]
```
Detalle del Byte Array:
| Byte  | Contenido                     |
| ----- | ----------------------------- |
| 0     | 0xAA                          |
| 1     | 0x55                          |
| 2     | TYPE (1 = subida, 2 = bajada) |
| 3..   | Datos (int16_t × N_SAMPLES)   |
| end-1 | 0x55                          |
| end   | 0xAA                          |
---
## Parámetros configurables (`config.h`)
Puedes modificar el comportamiento del firmware editando `main/config.h`:
```
C
#define I2S_SAMPLE_RATE     20000           // Frecuencia de muestreo (Hz)
#define N_SAMPLES           200             // Muestras por rampa
#define TRIGGER_PIN         GPIO_NUM_26     // Pin de entrada del Trigger
#define ADC_CHANNEL         ADC_CHANNEL_6   // Canal ADC (Corresponde a GPIO 34)
#define UART_BAUD_RATE      115200          // Velocidad UART
```
---
## Autores
Proyecto desarrollado para la asignatura Antenas Facultad de Ingeniería – Universidad de Cuenca Carrera de Ingeniería en Telecomunicaciones

Integrantes:

- Diego Portilla

- Christopher Carchipulla

- Mateo Lasso

- Emilio Nicolalde

- Erick Cajamarca