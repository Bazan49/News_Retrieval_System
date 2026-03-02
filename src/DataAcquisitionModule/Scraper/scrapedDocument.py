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
        html,
        # images,
        # content_hash,
        scraped_at,
        discovered_at,
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
        self.html = html
        # self.images = images
        # self.content_hash = content_hash
        self.scraped_at = scraped_at
        self.discovered_at = discovered_at
        self.indexed = indexed
        self.embeddings_generated = embeddings_generated
    