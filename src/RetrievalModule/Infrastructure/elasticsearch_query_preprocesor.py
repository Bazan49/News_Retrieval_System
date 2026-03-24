from typing import List
from RetrievalModule.Domain.query_preprocessor import QueryPreprocessor
from elasticsearch import AsyncElasticsearch

class ElasticsearchQueryPreprocessor(QueryPreprocessor):
    """
    Preprocesa consultas usando el mismo analizador que Elasticsearch utilizó
    para indexar los documentos.
    """
    def __init__(
        self,
        client: AsyncElasticsearch,
        index_name: str,
        analyzer: str = "spanish_analyzer"
    ):
        self.client = client
        self.index_name = index_name
        self.analyzer = analyzer

    async def preprocess(self, text: str) -> List[str]:
        """
        Devuelve la lista de tokens para la consulta.
        """
        if not text or not text.strip():
            return []

        response = await self.client.indices.analyze(
            index=self.index_name,  
            body={
                "analyzer": self.analyzer,
                "text": text
            }
        )
        # Extraer los tokens resultantes
        tokens = [token["token"] for token in response["tokens"]]
        return tokens