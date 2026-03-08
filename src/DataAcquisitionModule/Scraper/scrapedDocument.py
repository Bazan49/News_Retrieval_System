class ScrapedDocument:
    def __init__(
        self,
        source,
        url,
        url_normalized,
        title,
        content,
        authors,
        date,
        # content_hash,
        indexed,
        embeddings_generated
    ):
        self.source = source
        self.url = url
        self.url_normalized = url_normalized
        self.title = title
        self.content = content
        self.authors = authors
        self.date = date
        # self.content_hash = content_hash
        self.indexed = indexed
        self.embeddings_generated = embeddings_generated
    