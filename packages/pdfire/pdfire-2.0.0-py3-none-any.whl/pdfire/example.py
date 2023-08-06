from pdfire import Client, ConversionParams
from pdfire import errors

if __name__ == '__main__':
    client = Client('API-KEY')

    try:
        result = client.convert(ConversionParams(
            url='https://google.com',
            margin="100px"
        ))

        result.save_to('/conversion.pdf')
    except errors.RequestError as err:
        print(err)
