class Result:
    def bytes(self):
        """Get the PDF as bytes."""
        raise NotImplementedError("bytes method not implemented.")

    def save_to(self, path: str):
        """Save the PDF as a file at the given path."""
        with open(path, "wb") as f:
            f.write(self.bytes())
