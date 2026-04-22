class ScrapedDocument:
    def __init__(
        self,
        source,
        url,
        title,
        content,
        authors,
        date,
    ):
        self.source = source
        self.url = url
        self.title = title
        self.content = content
        self.authors = authors
        self.date = date
    