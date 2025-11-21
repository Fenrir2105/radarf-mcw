# ==============================================================================
# config/radar_config.py
# ==============================================================================
from dataclasses import dataclass

@dataclass
class RadarConfig:
    """Configuración centralizada del sistema FMCW"""
    # Parámetros del radar
    Fs: float = 40000           # Hz - Frecuencia de muestreo
    N: int = 256                # Número de muestras por rampa
    B: float = 250e6            # Hz - Ancho de banda
    c: float = 3e8              # m/s - Velocidad de la luz
    fc: float = 24e9            # Hz - Frecuencia central de la antena
    
    # Puertos seriales
    port_I: str = "COM5"
    port_Q: str = "COM8"
    port_display: str = "COM6"  # Puerto para Arduino/OLED
    baudrate: int = 115200
    timeout: float = 2.0
    baudrate_display: int = 115200        # Baudrate típico
    
    # Parámetros de procesamiento
    N_SAMPLES: int = 400
    velocity_threshold: float = 0.01  # m/s para detectar movimiento
    samples_per_ramp = 256 # Muestras a tomar para el procesamiento en cada rampa
    
    # Tamaños de colas
    queue_size: int = 5

    # Display
    enable_display: bool = True  # Habilitar/deshabilitar salida a OLED
    
    # Calculados
    @property
    def T(self) -> float:
        """Duración del chirp"""
        t =(1 / self.Fs) * self.N
        print(f"Tiempo de chirp {t}")
        return t
    
    @property
    def K(self) -> float:
        """Tasa de cambio de frecuencia"""
        return self.B / self.T















