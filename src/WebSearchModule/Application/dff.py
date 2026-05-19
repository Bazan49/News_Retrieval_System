async def _store_web_results(self, web_search_entities) -> None:
        """
        Procesa e indexa resultados de búsqueda web.
        
        Args:
            web_search_entities: Entidades WebSearchResult a almacenar
        """
        try:
            # Convertir a SearchDocument
            search_docs = self.document_processor.process_batch(web_search_entities)
            
            # Generar IDs cortos únicos para documentos web
            docs_with_ids = [
                (doc, self.document_processor.generate_short_id(doc.url))
                for doc in search_docs
            ]
            
            # Asegurar índice existe
            await self.index_repository.ensure_index()
            
            # Indexar en lote con IDs personalizados
            await self.index_repository.index_bulk_with_ids(docs_with_ids)
            
            # Refrescar índice
            await self.index_repository.refresh()
        except Exception as e:
            print(f"Error storing web results: {e}")