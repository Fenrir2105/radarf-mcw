

# ==============================================================================
# main.py
# ==============================================================================
import queue
from config.radar_config import RadarConfig
from hardware.serial_reader import SerialChannelReader
from hardware.display_writer import DisplayWriter
from processing.radar_processor import RadarProcessor
from visualization.plotter import RadarPlotter

def main():
    print("="*70)
    print("           SISTEMA FMCW RADAR I/Q ")
    print("="*70)
    
    # Configuración
    config = RadarConfig()
    
    # Colas de comunicación
    queue_I = queue.Queue(maxsize=config.queue_size)
    queue_Q = queue.Queue(maxsize=config.queue_size)
    queue_results = queue.Queue(maxsize=config.queue_size)
    queue_display = queue.Queue(maxsize=config.queue_size)
    
    # Crear componentes
    reader_I = SerialChannelReader(
        config.port_I, "I", config.baudrate, 
        config.timeout, config.N_SAMPLES, queue_I,
        config.samples_per_ramp
    )
    reader_Q = SerialChannelReader(
        config.port_Q, "Q", config.baudrate, 
        config.timeout, config.N_SAMPLES, queue_Q,
        config.samples_per_ramp
    )
    processor = RadarProcessor(config, queue_I, queue_Q, queue_results, queue_display)
    plotter = RadarPlotter(config, queue_results)

    # Crear display writer (opcional)  # ← NUEVO BLOQUE
    display_writer = None
    if config.enable_display:
        display_writer = DisplayWriter(
            config.port_display, 
            config.baudrate_display, 
            queue_display
        )
    
    # Iniciar sistema
    reader_I.start()
    reader_Q.start()
    processor.start()

    if display_writer: 
        display_writer.start()
    
    print("[MAIN] Sistema iniciado")
    if config.enable_display:  
        print(f"[MAIN] Display OLED habilitado en {config.port_display}")
    
    # Visualización (blocking)
    try:
        plotter.start()
    except KeyboardInterrupt:
        print("\n[MAIN] Deteniendo sistema...")
        reader_I.stop()
        reader_Q.stop()
        processor.stop()
        if display_writer:  
            display_writer.stop()
        print("[MAIN] Sistema detenido")

if __name__ == "__main__":
    main()