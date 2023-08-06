import datetime
import requests
from dateutil import parser
from pdfire import Result

class ConversionResult:
    size: int
    width: int
    height: int
    expires_at: datetime.datetime
    runtime: datetime.timedelta
    url: str

    def __init__(self, size: int, width: int, height: int, expires_at: datetime.datetime, runtime: datetime.timedelta, url: str):
        self.size = size
        self.width = width
        self.height = height
        self.expires_at = expires_at
        self.runtime = runtime
        self.url = url

class Conversion(Result):
    initialized_at: datetime.datetime
    finished_at: datetime.datetime
    status: str
    error: str
    result: ConversionResult

    _dlpdf: bytes

    def __init__(
        self,
        initialized_at: datetime.datetime,
        finished_at: datetime.datetime,
        status: str,
        error: str,
        result: ConversionResult
    ):
        self.initialized_at = initialized_at
        self.finished_at = finished_at
        self.status = status
        self.error = error
        self.result = result
        self._dlpdf = None

    def bytes(self):
        """Get the PDF as bytes."""
        if self._dlpdf is None:
            self._dlpdf = requests.get(self.result.url).content
        
        return self._dlpdf
