# ==============================================================================
# core/data_models.py
# ==============================================================================
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class ChannelData:
    """Datos de un canal (I o Q)"""
    channel_id: str  # 'I' o 'Q'
    up_samples: Optional[np.ndarray] = None
    down_samples: Optional[np.ndarray] = None
    timestamp: float = 0.0

@dataclass
class RadarResults:
    """Resultados del procesamiento I/Q complejo"""
    # Señales complejas
    signal_up_complex: np.ndarray
    signal_down_complex: np.ndarray
    
    # Espectros
    spec_up: np.ndarray
    spec_down: np.ndarray
    
    # Frecuencias detectadas
    f_up: float
    f_down: float
    
    # Resultados físicos
    distance: float
    velocity: float
    direction: str
    
    # Señales individuales para visualización
    I_up: np.ndarray
    Q_up: np.ndarray
    I_down: np.ndarray
    Q_down: np.ndarray