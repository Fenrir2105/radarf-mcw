# ==============================================================================
# hardware/display_writer.py
# ==============================================================================
import serial
import threading
import queue
import time
from core.data_models import RadarResults

class DisplayWriter:
    """Envía datos del radar a un display OLED via Arduino"""
    
    def __init__(self, port: str, baudrate: int, input_queue: queue.Queue):
        self.port = port
        self.baudrate = baudrate
        self.input_queue = input_queue
        self._running = False
        self._thread = None
        self._serial = None
    
    def start(self):
        """Inicia el hilo de escritura"""
        self._running = True
        self._thread = threading.Thread(target=self._write_loop, daemon=True)
        self._thread.start()
        print(f"[DISPLAY] Escritor iniciado en {self.port}")
    
    def stop(self):
        """Detiene el hilo de escritura"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._serial and self._serial.is_open:
            self._serial.close()
            print("[DISPLAY] Puerto cerrado")
    
    def _write_loop(self):
        """Loop principal de escritura"""
        try:
            # Abrir puerto serial
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1.0)
            time.sleep(2)  # Esperar a que Arduino reinicie después de conexión
            print(f"[DISPLAY] Conectado a Arduino en {self.port}")
            
            while self._running:
                try:
                    # Obtener resultados del radar
                    results = self.input_queue.get(timeout=0.5)
                    
                    # Formatear mensaje para Arduino
                    message = self._format_message(results)
                    
                    # Enviar por serial
                    self._serial.write(message.encode('utf-8'))
                    self._serial.flush()
                    
                    print(f"[DISPLAY] Enviado: {message.strip()}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[DISPLAY] Error al enviar: {e}")
        
        except serial.SerialException as e:
            print(f"[DISPLAY] ERROR: No se pudo abrir {self.port}: {e}")
        except Exception as e:
            print(f"[DISPLAY] ERROR: {e}")
        finally:
            if self._serial and self._serial.is_open:
                self._serial.close()
    
    def _format_message(self, results: RadarResults) -> str:
        """
        Formatea los datos para enviar al Arduino
        Protocolo: D:<distancia>,V:<velocidad>,DIR:<direccion>\n
        """
        # Formato simple para parsear en Arduino
        message = f"D:{results.distance:.2f},V:{results.velocity:.2f},DIR:{results.direction}\n"
        return message