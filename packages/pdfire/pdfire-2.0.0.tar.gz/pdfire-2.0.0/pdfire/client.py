import json
import requests
from typing import List
from dateutil import parser
from datetime import timedelta
from pdfire import ConversionParams, Result, BytesResult, Conversion, ConversionResult, errors

class Client:
    def __init__(self, api_key: str, base_url: str = 'https://api.pdfire.io/v1'):
        self.api_key = api_key
        self.base_url = base_url

    def convert(self, params) -> Result:
        """Send the conversion / merge parameters to the PDFire API and return the conversion result."""

        data = json.dumps(params.to_dict())
        response = requests.post(
            url = self.base_url + "/conversions",
            data = data,
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Content-Type': 'application/json',
            }
        )

        if response.status_code == 400:
            raise errors.InvalidRequestError(self._get_api_errors(response))

        if response.status_code == 401:
            raise errors.AuthenticationError(self._get_api_errors(response))
        
        if response.status_code == 402:
            raise errors.QuotaExceededError(self._get_api_errors(response))
    
        if response.status_code == 403:
            raise errors.ForbiddenActionError(self._get_api_errors(response))
            
        if response.status_code == 500:
            raise errors.ConversionError(self._get_api_errors(response))

        if response.status_code != 201:
            raise errors.RequestError(self._get_api_errors(response))

        return self._result(response)
    
    def convert_url(self, url: str, params: ConversionParams) -> Result:
        """Set the 'url' of the parameters, submit the request and return the result."""
        params.url = url
        return self.convert(params)
    
    def convert_html(self, html: str, params: ConversionParams) -> Result:
        """Set the 'html' of the parameters, submit the request and return the result."""
        params.html = html
        return self.convert(params)
    
    def convert_using_cdn(self, params) -> Conversion:
        """Set the 'cdn' field of the parameters to True, submit the request and return the conversion."""
        params.cdn = True
        return self.convert(params)
    
    def convert_using_storage(self, params, storage = True) -> Conversion:
        """Enable the 'storage' option, submit the request and return the conversion."""
        params.storage = storage
        return self.convert(params)
    
    def convert_to_bytes(self, params) -> BytesResult:
        """Set the 'cdn' field of the parameters to False, submit the request and return the conversion."""
        params.cdn = False
        return self.convert(params)

    def _result(self, response: requests.Response) -> Result:
        content_type = response.headers["Content-Type"]

        if "application/json" in content_type:
            return self._cdn_result(response)
        
        return self._bytes_result(response)
    
    def _cdn_result(self, response: requests.Response) -> Conversion:
        data = response.json()

        conversion_result = None

        if not data['result'] is None:
            conversion_result = ConversionResult(
                data['result']['size'],
                data['result']['width'],
                data['result']['height'],
                parser.parse(data['result']['expiresAt']),
                timedelta(milliseconds=data['result']['runtime']),
                data['result']['url']
            )

        return Conversion(
            parser.parse(data['createdAt']),
            parser.parse(data['convertedAt']) if not data['convertedAt'] is None else None,
            data['status'],
            data['error'],
            conversion_result
        )
    
    def _bytes_result(self, response: requests.Response) -> BytesResult:
        return BytesResult(pdf=response.content)
    
    def _get_api_errors(self, response: requests.Response) -> List[errors.ApiError]:
        data = response.json()
        errors_data = data['errors'] if data['errors'] else []
        return map(lambda err: errors.ApiError(err['message']), errors_data)
