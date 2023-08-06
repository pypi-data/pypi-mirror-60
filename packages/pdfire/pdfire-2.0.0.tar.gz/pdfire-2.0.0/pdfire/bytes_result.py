from pdfire import Result

class BytesResult(Result):
    def __init__(self, pdf):
        self.pdf = pdf

    def bytes(self):
        """Get the PDF as bytes."""
        return self.pdf
