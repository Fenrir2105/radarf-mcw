# ==============================================================================
# processing/radar_processor.py
# ==============================================================================
import threading
import queue
import numpy as np
from core.data_models import ChannelData, RadarResults
from core.signal_processing import SignalProcessor
from config.radar_config import RadarConfig

class RadarProcessor:
    """Procesador central que combina canales I/Q"""
    
    def __init__(self, config: RadarConfig, queue_I: queue.Queue, 
                 queue_Q: queue.Queue, queue_results: queue.Queue,
                 queue_display: queue.Queue):
        self.config = config
        self.queue_I = queue_I
        self.queue_Q = queue_Q
        self.queue_results = queue_results
        self.queue_display = queue_display
        self.signal_processor = SignalProcessor(config.Fs)
        self._running = False
        self._thread = None
    
    def start(self):
        """Inicia el procesamiento"""
        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        print("[PROC] Procesador iniciado")
    
    def stop(self):
        """Detiene el procesamiento"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _process_loop(self):
        """Loop principal de procesamiento"""
        data_I = None
        data_Q = None
        
        while self._running:
            # Obtener datos de ambos canales
            try:
                data_I = self.queue_I.get(timeout=0.1)
                print("[PROC] Datos I recibidos")
            except queue.Empty:
                pass
            
            try:
                data_Q = self.queue_Q.get(timeout=0.1)
                print("[PROC] Datos Q recibidos")
            except queue.Empty:
                pass
            
            # Procesar cuando tengamos ambos
            if data_I is not None and data_Q is not None:
                results = self._process_iq_data(data_I, data_Q)
                self._publish_results(results)
                data_I = None
                data_Q = None
    
    def _process_iq_data(self, data_I: ChannelData, data_Q: ChannelData) -> RadarResults:
        """Procesa datos I/Q y calcula parámetros"""
        print("[PROC] Procesando señal compleja I+jQ...")
        
        # Construir señales complejas
        signal_up_complex = data_I.up_samples + 1j * data_Q.up_samples
        signal_down_complex = data_I.down_samples + 1j * data_Q.down_samples
        
        # Análisis espectral
        f_up, spec_up, _ = self.signal_processor.get_peak_freq_complex(signal_up_complex)
        f_down, spec_down, _ = self.signal_processor.get_peak_freq_complex(signal_down_complex)
        
        # Calcular parámetros físicos
        velocity = self.signal_processor.calculate_velocity(
            f_up, f_down, self.config.c, self.config.fc
        )
        distance = self.signal_processor.calculate_distance(
            f_up, f_down, self.config.c, self.config.K
        )
        direction = self.signal_processor.determine_direction(
            f_up , f_down
        )
        
        # Imprimir resultados
        self._print_results(f_up, f_down, distance, velocity, direction)
        
        return RadarResults(
            signal_up_complex=signal_up_complex,
            signal_down_complex=signal_down_complex,
            spec_up=spec_up,
            spec_down=spec_down,
            f_up=f_up,
            f_down=f_down,
            distance=distance,
            velocity=velocity,
            direction=direction,
            I_up=data_I.up_samples,
            Q_up=data_Q.up_samples,
            I_down=data_I.down_samples,
            Q_down=data_Q.down_samples
        )
    
    def _print_results(self, f_up, f_down, distance, velocity, direction):
        """Imprime resultados formateados"""
        print("\n" + "="*70)
        print("              RESULTADOS RADAR FMCW (I/Q)")
        print("="*70)
        print(f"Frecuencia Up-chirp   (f_up)   = {f_up:10.2f} Hz")
        print(f"Frecuencia Down-chirp (f_down) = {f_down:10.2f} Hz")
        print(f"\n{'DISTANCIA':^35} = {distance:10.4f} m")
        print(f"{'VELOCIDAD':^35} = {velocity:10.4f} m/s")
        print(f"{'DIRECCIÓN':^35} = {direction:^10}")
        print("="*70 + "\n")
    
    def _publish_results(self, results: RadarResults):
        """Envía resultados a visualización"""
        try:
            self.queue_results.put(results, block=False)
        except queue.Full:
            try:
                self.queue_results.get_nowait()
                self.queue_results.put(results, block=False)
            except:
                pass

        # Enviar a display OLED (si está habilitado)  # ← AGREGAR TODO ESTE BLOQUE
        if self.queue_display is not None:
            try:
                self.queue_display.put(results, block=False)
            except queue.Full:
                try:
                    self.queue_display.get_nowait()
                    self.queue_display.put(results, block=False)
                except:
                    pass