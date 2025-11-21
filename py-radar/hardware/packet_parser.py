# ==============================================================================
# hardware/packet_parser.py
# ==============================================================================
import serial
import numpy as np
from struct import unpack
from typing import Optional, Tuple

class PacketParser:
    """Parsea paquetes del protocolo del radar"""
    
    HEADER_START = (0xAA, 0x55)
    FOOTER_END = (0x55, 0xAA)
    
    def __init__(self, n_samples: int):
        self.n_samples = n_samples
    
    def read_packet(self, ser: serial.Serial) -> Tuple[Optional[int], Optional[np.ndarray]]:
        """Lee un paquete del puerto serial"""
        # Buscar header
        while True:
            if ser.read(1) == bytes([self.HEADER_START[0]]) and \
               ser.read(1) == bytes([self.HEADER_START[1]]):
                break
        
        # Leer tipo de paquete
        pkt_type = ser.read(1)[0]
        
        # Leer datos
        data = ser.read(self.n_samples * 2)
        if len(data) != self.n_samples * 2:
            return None, None
        samples = np.array(unpack("<" + "h" * self.n_samples, data), dtype=np.float32)
        
        # Verificar footer
        footer1 = ser.read(1)
        footer2 = ser.read(1)

        if not (footer1 == bytes([self.FOOTER_END[0]]) and 
                footer2 == bytes([self.FOOTER_END[1]])):
            return None, None
        
        return pkt_type, samples