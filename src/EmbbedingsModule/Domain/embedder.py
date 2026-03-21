from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseEmbedder(ABC):
    """Interfaz para generadores de embeddings."""
    
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Genera embeddings para múltiples textos."""
        pass
    
    @abstractmethod
    def encode_single(self, text: str) -> np.ndarray:
        """Embedding para un solo texto."""
        pass
    
    @abstractmethod
    def dim(self) -> int:
        """Dimensionalidad de los embeddings."""
        pass
