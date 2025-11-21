# ==============================================================================
# visualization/plotter.py
# ==============================================================================
import matplotlib.pyplot as plt
import numpy as np
import queue
from core.data_models import RadarResults
from config.radar_config import RadarConfig

class RadarPlotter:
    """Visualización de datos del radar"""
    
    def __init__(self, config: RadarConfig, queue_results: queue.Queue):
        self.config = config
        self.queue_results = queue_results
        self.fig = None
    
    def start(self):
        """Inicia la visualización (blocking)"""
        print("[VIS] Iniciando visualización")
        plt.ion()
        self.fig = plt.figure(figsize=(16, 6))
        self._plot_loop()
    
    def _plot_loop(self):
        """Loop principal de graficación"""
        while True:
            try:
                results = self.queue_results.get(timeout=0.5)
                self._plot_results(results)
            except queue.Empty:
                plt.pause(0.1)
                continue
    
    def _plot_results(self, results: RadarResults):
        """Genera todas las gráficas"""
        plt.clf()
        
        # Concatenar señales I/Q (subida + bajada)
        I_complete = np.concatenate([results.I_up, results.I_down])
        Q_complete = np.concatenate([results.Q_up, results.Q_down])
        t_complete = np.arange(len(I_complete)) / self.config.Fs * 1000  # ms
        
        # Señal I/Q concatenada en tiempo (ocupa fila completa superior)
        self._plot_iq_time_complete(t_complete, I_complete, Q_complete, results)
        
        # Diagramas IQ
        self._plot_iq_diagram(results, row=3, chirp='up',col=0)
        self._plot_iq_diagram(results, row=3, chirp='down', col=1)
        
        # FFT
        self._plot_fft(results, chirp='up', subplot_idx=4)
        self._plot_fft(results, chirp='down', subplot_idx=5)
        
        # Panel de resultados
        self._plot_results_panel(results)
        
        plt.tight_layout()
        plt.pause(0.01)
    
    
    def _plot_iq_time_complete(self, t, I_complete, Q_complete, results):
        """Gráfica I/Q concatenadas vs tiempo (Subida + Bajada)"""
        ax = plt.subplot2grid((4, 3), (0, 0), colspan=2)
        
        # Plotear señales completas
        ax.plot(t, I_complete, 'b-', label='I', linewidth=1)
        ax.plot(t, Q_complete, 'r-', label='Q', linewidth=1)
        ax.set_ylim(0,4096)
        
        # Marcar la transición entre subida y bajada
        transition_time = len(results.I_up) / self.config.Fs * 1000
        ax.axvline(transition_time, color='gray', linestyle='--', 
                   linewidth=2, alpha=0.5, label='Transición Up→Down')
        
        # Sombrear regiones
        ax.axvspan(0, transition_time, alpha=0.1, color='green', label='Up-chirp')
        ax.axvspan(transition_time, t[-1], alpha=0.1, color='magenta', label='Down-chirp')
        
        ax.set_title("Señales I/Q Completas (Up-chirp + Down-chirp)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Tiempo [ms]")
        ax.set_ylabel("Amplitud")
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

    def _plot_fft_channel(self, signal, freq_peak, channel_name, chirp, subplot_idx):
        """Gráfica FFT de un canal individual (I o Q)"""
        ax = plt.subplot(4, 3, subplot_idx)
        
        # Calcular FFT
        signal = signal - np.mean(signal)
        window = np.hanning(len(signal))
        spectrum = np.fft.fft(signal * window, n=1024)  # Zero padding a 1024
        spectrum = np.fft.fftshift(spectrum)
        magnitude = np.abs(spectrum)
        
        # Vector de frecuencias
        freqs = np.fft.fftshift(np.fft.fftfreq(1024, 1/self.config.Fs))
        
        # Plotear
        color = 'b' if channel_name == 'I' else 'r'
        ax.plot(freqs, magnitude, color=color, linewidth=1.5)
        ax.axvline(freq_peak, color='orange', linestyle='--', linewidth=2, 
                   label=f'f={freq_peak:.2f} Hz')
        ax.set_title(f"FFT Canal {channel_name} - {chirp.capitalize()}-chirp")
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("Magnitud")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_iq_diagram(self, results, row, chirp='up', col=0):
        """Diagrama I vs Q"""
        plt.subplot(5, 3, row*3 + col + 1)
        I = results.I_up if chirp == 'up' else results.I_down
        Q = results.Q_up if chirp == 'up' else results.Q_down
        color = 'g' if chirp == 'up' else 'm'
        plt.plot(I, Q, f'{color}-', linewidth=0.5, alpha=0.5)
        plt.plot(I[0], Q[0], 'go', markersize=8, label='Inicio')
        plt.plot(I[-1], Q[-1], 'ro', markersize=8, label='Fin')
        plt.title(f"Diagrama I/Q - {chirp.capitalize()}-chirp")
        plt.xlabel("I")
        plt.ylabel("Q")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
    
    def _plot_fft(self, results, chirp, subplot_idx):
        """Gráfica FFT"""
        plt.subplot(4, 3, subplot_idx)
        signal = results.signal_up_complex if chirp == 'up' else results.signal_down_complex
        spec = results.spec_up if chirp == 'up' else results.spec_down
        freq = results.f_up if chirp == 'up' else results.f_down
        
        freqs = np.fft.fftshift(np.fft.fftfreq(len(spec), 1/self.config.Fs))
        plt.plot(freqs, spec, 'b-', linewidth=1.5)
        plt.axvline(freq, color='r', linestyle='--', linewidth=2, 
                   label=f'f={freq:.2f} Hz')
        plt.title(f"FFT {chirp.capitalize()}-chirp | f={freq:.2f} Hz")
        plt.xlabel("Frecuencia [Hz]")
        plt.ylabel("Magnitud")
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    def _plot_results_panel(self, results):
        """Panel de resultados"""
        ax = plt.subplot2grid((3, 3), (0, 2), rowspan=3)
        ax.axis('off')
        
        if results.direction == "ACERCÁNDOSE":
            color = "#FF6B6B"
            arrow = "←"
        elif results.direction == "ALEJÁNDOSE":
            color = "#4ECDC4"
            arrow = "→"
        else:
            color = "#95E1D3"
            arrow = "↔"
        
        text = f"""
╔════════════════════════════════════════════╗
║      RADAR FMCW - PROCESAMIENTO I/Q       ║
╠════════════════════════════════════════════╣
║                                            ║
║  f_up   = {results.f_up:10.2f} Hz              ║
║  f_down = {results.f_down:10.2f} Hz              ║
║                                            ║
║  DISTANCIA:  {results.distance:8.4f} m             ║
║  VELOCIDAD:  {results.velocity:8.4f} m/s           ║
║  DIRECCIÓN:  {arrow} {results.direction:^15} {arrow}      ║
║                                            ║
╚════════════════════════════════════════════╝
        """
        
        ax.text(0.5, 0.5, text, ha='center', va='center',
               fontfamily='monospace', fontsize=12,
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.3,
                        edgecolor=color, linewidth=3))
