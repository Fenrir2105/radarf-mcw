# ==============================================================================
# hardware/serial_reader.py
# ==============================================================================
import serial
import threading
import queue
from typing import Callable
from core.data_models import ChannelData
from hardware.packet_parser import PacketParser

class SerialChannelReader:
    """Lee datos de un canal serial de forma asíncrona"""
    
    def __init__(self, port: str, channel_name: str, baudrate: int, 
                 timeout: float, n_samples: int, output_queue: queue.Queue, samples_per_ramp: int = 128):
        self.port = port
        self.channel_name = channel_name
        self.baudrate = baudrate
        self.timeout = timeout
        self.output_queue = output_queue
        self.parser = PacketParser(n_samples)
        self._running = False
        self._thread = None
        self.sampler_per_ramp = samples_per_ramp
    
    def start(self):
        """Inicia el hilo de lectura"""
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        print(f"[{self.channel_name}] Lector iniciado en {self.port}")
    
    def stop(self):
        """Detiene el hilo de lectura"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _read_loop(self):
        """Loop principal de lectura"""
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            channel_data = ChannelData(channel_id=self.channel_name)
            
            while self._running:
                pkt_type, samples = self.parser.read_packet(ser)
                if samples is None:
                    continue
                
                if pkt_type == 1:  # SUBIDA
                    channel_data.up_samples = samples[:self.sampler_per_ramp]
                    print(f"[{self.channel_name}] Rampa SUBIDA recibida")
                
                elif pkt_type == 2:  # BAJADA
                    channel_data.down_samples = samples[-self.sampler_per_ramp:]
                    print(f"[{self.channel_name}] Rampa BAJADA recibida")
                
                # Enviar cuando tengamos ambas rampas
                if channel_data.up_samples is not None and \
                   channel_data.down_samples is not None:
                    self._send_data(channel_data)
                    channel_data = ChannelData(channel_id=self.channel_name)
        
        except serial.SerialException as e:
            print(f"[{self.channel_name}] ERROR Serial: {e}")
        except Exception as e:
            print(f"[{self.channel_name}] ERROR: {e}")
    
    def _send_data(self, data: ChannelData):
        """Envía datos a la cola de procesamiento"""
        try:
            self.output_queue.put(data, block=False)
            print(f"[{self.channel_name}] Datos enviados a procesamiento")
        except queue.Full:
            print(f"[{self.channel_name}] WARNING: Cola llena")
            try:
                self.output_queue.get_nowait()
                self.output_queue.put(data, block=False)
            except:
                pass
