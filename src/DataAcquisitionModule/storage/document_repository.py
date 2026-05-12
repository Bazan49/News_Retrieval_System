from abc import ABC, abstractmethod

class IDocumentRepository(ABC):

    @abstractmethod
    def save(self, document):
        """Guarda un documento (puede ser en memoria o persistente)"""
        pass

    @abstractmethod
    def flush(self):
        """Asegura persistencia física (si aplica)"""
        pass

    @abstractmethod
    def load(self):
        """Carga documentos desde almacenamiento"""
        pass
