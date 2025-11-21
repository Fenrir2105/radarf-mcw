# Sistema FMCW Radar I/Q — Procesamiento Modular

## Proyecto de la materia de Antenas — Universidad de Cuenca  
Carrera de Ingeniería en Telecomunicaciones

### Autores
- Diego Portilla
- Christopher Carchipulla
- Mateo Lasso
- Emilio Nicolalde
- Erick Cajamarca

---

## 🛰️ Descripción General

Sistema FMCW Radar I/Q - Procesamiento Modular es un proyecto académico que implementa un radar FMCW (Frequency Modulated Continuous Wave) capaz de realizar procesamiento en tiempo real para la detección de distancia, velocidad y dirección de objetos mediante análisis espectral de señales complejas I/Q.

El sistema combina hardware embebido (Arduino y ESP32) con un módulo de procesamiento en Python para ofrecer una arquitectura flexible, modular y escalable para experimentación y pruebas en laboratorio.

---

## 📂 Estructura del Repositorio

/
├── arduino/
│   └── Código para el módulo AD933:
│       • Generación de rampa triangular FMCW
│       • Recepción de parámetros desde el sistema Python
│
├── idf-radar/
│   └── Proyecto basado en ESP-IDF para ESP32:
│       • Muestreo de señales I y Q provenientes de la antena
│       • Comunicación con el sistema de procesamiento
│
├── py-radar/
│   └── Proyecto principal en Python:
│       • Procesamiento digital de señales I/Q
│       • FFT, filtrado, detección de picos
│       • Estimación de distancia y velocidad
│       • Interfaz modular para control del sistema
│
└── README.md

---

## ⚙️ Funcionamiento del Sistema

1. **Generación de señal FMCW (Arduino + AD933)**  
   - Se genera una rampa triangular que modula en frecuencia la señal transmitida.
   - Los parámetros del barrido pueden ser enviados desde Python.

2. **Muestreo de señales I/Q (ESP32 con ESP-IDF)**  
   - Los ESP32 capturan las señales I y Q provenientes del mezclador.
   - Los datos se envían al módulo Python.

3. **Procesamiento de Señales (Python)**  
   - Aplicación de ventanas, FFT, filtrado y demodulación compleja.
   - Cálculo de:
     - Distancia mediante beat frequency
     - Velocidad mediante análisis Doppler
     - Dirección del objetivo (si aplica)
   - Visualización y análisis espectral.

---

## 🛠️ Tecnologías Utilizadas

- Arduino (control del AD933)
- ESP32 con ESP-IDF (adquisición de señales I/Q)
- Python 3.x  
  - NumPy  
  - SciPy  
  - Matplotlib  
  - Herramientas de DSP

---

## 📡 Objetivos del Proyecto

- Implementar un sistema FMCW funcional a nivel académico.
- Comprender el procesamiento I/Q y su aplicación para detección de movimiento.
- Desarrollar una arquitectura modular separando:
  - Generación del chirp
  - Adquisición de señales I/Q
  - Procesamiento digital
- Permitir futuras extensiones como beamforming.

---

## 🚀 Cómo Empezar

### 1. Arduino
Carga el código del directorio `arduino/` en el módulo encargado del AD933.

### 2. ESP-IDF (ESP32)
Compila y flashea el proyecto de `idf-radar/` en los ESP32.

### 3. Python
Instala dependencias y ejecuta:
```
cd py-radar
pip install -r requirements.txt
python main.py
```

---




