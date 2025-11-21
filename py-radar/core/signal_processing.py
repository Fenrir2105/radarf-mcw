# ==============================================================================
# core/signal_processing.py
# ==============================================================================
import numpy as np
from typing import Tuple

class SignalProcessor:
    """Procesamiento de señales de radar FMCW"""
    
    def __init__(self, fs: float):
        self.fs = fs
        self.fft_size = 1024 # Usado para agregar Zero Padding, ya que entran menos muestras
    
    def get_peak_freq_complex(self, signal_complex: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        Calcula la frecuencia pico de una señal compleja
        Returns: (frecuencia_pico, magnitud_espectro, vector_frecuencias)
        """
        # Remover DC
        signal_complex = signal_complex - np.mean(signal_complex)
        
        # Ventana
        window = np.hanning(len(signal_complex))
        
        # FFT completa
        spectrum = np.fft.fft(signal_complex * window, n=self.fft_size)
        spectrum = np.fft.fftshift(spectrum)
        
        # Magnitud
        magnitude = np.abs(spectrum)
        
        # Buscar pico
        peak_bin = np.argmax(magnitude)
        
        # Calcular frecuencia
        freqs = np.fft.fftshift(np.fft.fftfreq(self.fft_size, 1/self.fs))
        freq = freqs[peak_bin]
        
        return np.abs(freq), magnitude, freqs
    
    @staticmethod
    def calculate_distance(f_up: float, f_down: float, c: float, K: float) -> float:
        """Calcula distancia: R = (f_up + f_down) * c / (4*K)"""
        return (f_up + f_down) * c / (4*3 * K)
    
    @staticmethod
    def calculate_velocity(f_up: float, f_down: float, c: float, f: float) -> float:
        """Calcula velocidad: v = (f_down - f_up)* c / (4 * f)"""
        return (f_up - f_down) * c / (4 * f)
    
    @staticmethod
    def determine_direction(fd: float, fu: float) -> str:
        """Determina dirección basado en velocidad"""
        if fd > fu:
            return "ACERCÁNDOSE"
        elif fd < fu:
            return "ALEJÁNDOSE"
        else:
            return "ESTATICO"
