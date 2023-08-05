import requests

from zonesmart.utils import logger

logger = logger.get_logger("converter")


class CurrencyConverterAPIError(Exception):
    pass


def convert_currency_make_request(
    from_currency, to_currency, token="dc99c91c321fcce31879"
):
    resource = f"http://free.currencyconverterapi.com/api/v5/"
    q = f"{from_currency}_{to_currency}"
    query = f"convert?q={q}&compact=ultra&apiKey={token}"
    url = resource + query
    response = requests.get(url=url)
    try:
        response.raise_for_status()
    except requests.HTTPError as err:
        message = (
            f"Не удалось конвертировать валюту ({from_currency}-->{to_currency})\n{err}"
        )
        logger.critical(message)
        raise CurrencyConverterAPIError(message)
    return response.json()[q]


def convert_amount(from_currency, to_currency, value):
    return value * convert_currency_make_request(from_currency, to_currency)


def to_meter(value, unit):
    if unit == "METER":
        return value
    elif unit == "CENTIMETER":
        return value * 0.01
    elif unit == "INCH":
        return value * 0.0254
    elif unit == "FEET":
        return value * 0.3048
    else:
        raise AttributeError(f"Единица измерения не поддерживается ({unit})")


def to_kilogram(value, unit):
    if unit == "KILOGRAM":
        return value
    elif unit == "GRAM":
        return value * 0.001
    elif unit == "OUNCE":
        return value * 0.0283495
    elif unit == "POUND":
        return value * 0.453592
    else:
        raise AttributeError(f"Единица измерения не поддерживается ({unit})")
