# Módulo Arduino — Control del AD9833 y Visualización OLED

Este directorio contiene el firmware del Arduino encargado de:
- Generar la señal triangular moduladora del radar usando el AD9833  
- Recibir desde Python los datos procesados (distancia, velocidad, dirección)  
- Mostrar la información en una pantalla OLED SSD1306  

Forma parte del proyecto completo **Sistema FMCW Radar I/Q – Procesamiento Modular**.

---

## Funcionalidad del Módulo

El Arduino cumple tres funciones principales:

### 1. Generación de la señal FMCW (AD9833)
- Configuración del AD9833 en modo **triangular**
- Ajuste de frecuencia mediante un potenciómetro conectado a `A0`
- Emisión continua del chirp para el radar

### 2. Recepción de datos procesados desde Python
El módulo recibe mensajes seriales con el formato:
```
D:12.34,V:1.23,DIR:F
```

Donde:  
- `D` → distancia en metros  
- `V` → velocidad en m/s  
- `DIR` → dirección detectada (F = acercándose, B = alejándose)

### 3. Visualización en pantalla OLED SSD1306
- Muestra distancia, velocidad y dirección en tiempo real
- Usa comunicación I2C (dirección 0x3C)

---

## Estructura del Código

El firmware se divide en los siguientes bloques:

| Bloque | Descripción |
|--------|-------------|
| **Configuración OLED** | Inicializa la pantalla SSD1306 usando Adafruit GFX |
| **Control AD9833** | Maneja la generación de la rampa triangular |
| **Lógica de frecuencia** | Lee el potenciómetro y ajusta la frecuencia |
| **Lectura Serial** | Recibe y parsea los mensajes enviados por Python |
| **Render OLED** | Dibuja distancia, velocidad y dirección en pantalla |

---

## Conexiones de Hardware

### AD9833 (SPI)
| Señal | Arduino |
|-------|---------|
| FSYNC | D10 |
| CLK   | D13 |
| DATA  | D11 |

### OLED SSD1306 (I2C)
| Señal | Arduino |
|-------|---------|
| SDA   | A4 |
| SCL   | A5 |
| Dirección | 0x3C |

### Otros
| Componente | Pin |
|------------|-----|
| Potenciómetro | A0 |
| LED interno | D13 |

---

## Librerías Necesarias

Instalar desde el **Library Manager** del Arduino IDE:

- **MD_AD9833** (control del AD9833)
- **Adafruit GFX Library**
- **Adafruit SSD1306**
- **SPI.h** (incluida con Arduino)
- **Wire.h** (incluida con Arduino)

---

## Ejecución

1. Conecta el AD9833 y la pantalla según la tabla superior.  
2. Carga el sketch en tu placa Arduino.  
3. Abre el monitor serial a **115200 baud**.  
4. Envía desde Python los datos de radar.  
5. La pantalla OLED mostrará en tiempo real:
```
RADAR DOPPLER

Dist: 12.34 m
Vel: 1.23 m/s
Dir: F
```
---

## Formato de Comunicación Serial

El módulo espera líneas terminadas en `\n`:
```
D:<distancia>,V:<velocidad>,DIR:<direccion>
```
Ejemplo:
```
D:8.52,V:0.76,DIR:B
```

---

## Autores

Proyecto del grupo de estudiantes de la materia **Antenas**,  
Universidad de Cuenca – Ingeniería en Telecomunicaciones:

- Diego Portilla  
- Christopher Carchipulla  
- Mateo Lasso  
- Emilio Nicolalde  
- Erick Cajamarca  

---










