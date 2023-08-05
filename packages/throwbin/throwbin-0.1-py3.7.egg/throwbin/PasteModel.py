class PasteModel:
    def __init__(self, status: str, id: str):
        self.status = status
        self.id = id
        self.link = "http://throwbin.io/" + id
