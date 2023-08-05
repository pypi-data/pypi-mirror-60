# -*- coding: utf-8 -*-
from __future__ import absolute_import

import base64
import datetime
import hashlib
import hmac
import re
from time import gmtime, strftime

from requests import request
from requests.exceptions import HTTPError

from . import utils

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
try:
    from xml.etree.ElementTree import ParseError as XMLError
except ImportError:
    from xml.parsers.expat import ExpatError as XMLError


__all__ = [  # noqa F822
    "Feeds",
    "Inventory",
    "InboundShipments",
    "MWSError",
    "Reports",
    "Orders",
    "Products",
    "Recommendations",
    "Sellers",
    "Finances",
]


MARKETPLACES = {
    "CA": "https://mws.amazonservices.ca",  # A2EUQ1WTGCTBG2
    "US": "https://mws.amazonservices.com",  # ATVPDKIKX0DER",
    "DE": "https://mws-eu.amazonservices.com",  # A1PA6795UKMFR9
    "ES": "https://mws-eu.amazonservices.com",  # A1RKKUPIHCS9HS
    "FR": "https://mws-eu.amazonservices.com",  # A13V1IB3VIYZZH
    "IN": "https://mws.amazonservices.in",  # A21TJRUUN4KGV
    "IT": "https://mws-eu.amazonservices.com",  # APJ6JRA9NG5V4
    "UK": "https://mws-eu.amazonservices.com",  # A1F83G8C2ARO7P
    "JP": "https://mws.amazonservices.jp",  # A1VC38T7YXB528
    "CN": "https://mws.amazonservices.com.cn",  # AAHKV2X7AFYLW
    "MX": "https://mws.amazonservices.com.mx",  # A1AM78C64UM0Y8
    "AU": "https://mws.amazonservices.com.au",  # A39IBJ37TRP1C6
    "BR": "https://mws.amazonservices.com",  # A2Q3Y263D00KWC
}


class MWSError(Exception):
    """
    Main MWS Exception class
    """

    # Allows quick access to the response object.
    # Do not rely on this attribute, always check if its not None.
    response = None


def calc_md5(string):
    """
    Calculates the MD5 encryption for the given string
    """
    md5_hash = hashlib.md5()
    md5_hash.update(string)
    return base64.b64encode(md5_hash.digest()).strip(b"\n")


def calc_request_description(params):
    request_description = ""
    for key in sorted(params):
        encoded_value = quote(params[key], safe="-_.~")
        request_description += "&{}={}".format(key, encoded_value)
    return request_description[1:]  # don't include leading ampersand


def remove_empty(dict_):
    """
    Returns dict_ with all empty values removed.
    """
    return {k: v for k, v in dict_.items() if v}


def remove_namespace(xml):
    """
    Strips the namespace from XML document contained in a string.
    Returns the stripped string.
    """
    regex = re.compile(' xmlns(:ns2)?="[^"]+"|(ns2:)|(xml:)')
    return regex.sub("", xml)


class DictWrapper:
    def __init__(self, xml, rootkey=None):
        self.original = xml
        self.response = None
        self._rootkey = rootkey
        self._mydict = utils.XML2Dict().fromstring(remove_namespace(xml))
        self._response_dict = self._mydict.get(
            list(self._mydict.keys())[0], self._mydict
        )

    @property
    def parsed(self):
        if self._rootkey:
            return self._response_dict.get(self._rootkey)
        return self._response_dict


class DataWrapper:
    """
    Text wrapper in charge of validating the hash sent by Amazon.
    """

    def __init__(self, data, header):
        self.original = data
        self.response = None
        if "content-md5" in header:
            hash_ = calc_md5(self.original)
            if header["content-md5"].encode() != hash_:
                raise MWSError("Wrong Contentlength, maybe amazon error...")

    @property
    def parsed(self):
        return self.original


class MWS:
    """
    Base Amazon API class
    """

    URI = "/"
    VERSION = "2009-01-01"
    NAMESPACE = ""
    NEXT_TOKEN_OPERATIONS = []
    ACCOUNT_TYPE = "SellerId"

    def __init__(
        self,
        access_key,
        secret_key,
        account_id,
        region="US",
        domain="",
        uri="",
        version="",
        auth_token="",
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.auth_token = auth_token
        self.version = version or self.VERSION
        self.uri = uri or self.URI

        if domain:
            self.domain = domain
        elif region in MARKETPLACES:
            self.domain = MARKETPLACES[region]
        else:
            error_msg = (
                "Incorrect region supplied ('%(region)s'). Must be one of the following: %(marketplaces)s"
                % {"marketplaces": ", ".join(MARKETPLACES.keys()), "region": region,}
            )
            raise MWSError(error_msg)

    def get_params(self):
        """
        Get the parameters required in all MWS requests
        """
        params = {
            "AWSAccessKeyId": self.access_key,
            self.ACCOUNT_TYPE: self.account_id,
            "SignatureVersion": "2",
            "Timestamp": self.get_timestamp(),
            "Version": self.version,
            "SignatureMethod": "HmacSHA256",
        }
        if self.auth_token:
            params["MWSAuthToken"] = self.auth_token
        return params

    def make_request(self, extra_data, method="GET", **kwargs):  # noqa: C901
        """
        Make request to Amazon MWS API with these parameters
        """
        # Remove all keys with an empty value because
        # Amazon's MWS does not allow such a thing.
        extra_data = remove_empty(extra_data)

        # convert all Python date/time objects to isoformat
        for key, value in extra_data.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                extra_data[key] = value.isoformat()

        params = self.get_params()
        params.update(extra_data)
        request_description = calc_request_description(params)
        signature = self.calc_signature(method, request_description)
        url = "{domain}{uri}?{description}&Signature={signature}".format(
            domain=self.domain,
            uri=self.uri,
            description=request_description,
            signature=quote(signature),
        )
        # print(url)
        headers = {"User-Agent": "python-amazon-mws/0.8.6 (Language=Python)"}
        headers.update(kwargs.get("extra_headers", {}))
        is_success = False
        message = ""
        objects = {}
        try:
            response = request(
                method, url, data=kwargs.get("body", ""), headers=headers
            )
            response.raise_for_status()

            data = response.content
            rootkey = kwargs.get("rootkey", extra_data.get("Action") + "Result")
            try:
                try:
                    parsed_response = DictWrapper(data, rootkey)
                except TypeError:  # raised when using Python 3 and trying to remove_namespace()
                    # When we got CSV as result, we will got error on this
                    parsed_response = DictWrapper(response.text, rootkey)
            except XMLError:
                parsed_response = DataWrapper(data, response.headers)
        except HTTPError as e:
            message = str(e.response.text)
            objects = {
                "response": e.response,
                "parsed_message": DictWrapper(message).parsed,
            }
        except Exception as err:
            if err.__class__.__name__ == "ParseError":
                parsed_response = DataWrapper(data, header={})
                parsed_response.original = parsed_response.original.decode()
                is_success = True
            else:
                raise err
        else:
            is_success = True
        if is_success:
            message = "Запрос успешно выполнен."
            parsed_response.response = response
            objects = {"response": parsed_response}
        return is_success, message, objects

    def get_service_status(self):
        """
        Returns a GREEN, GREEN_I, YELLOW or RED status.
        Depending on the status/availability of the API its being called from.
        """
        return self.make_request(extra_data=dict(Action="GetServiceStatus"))

    def action_by_next_token(self, action, next_token):
        """
        Run a '...ByNextToken' action for the given action.
        If the action is not listed in self.NEXT_TOKEN_OPERATIONS, MWSError is raised.
        Action is expected NOT to include 'ByNextToken'
        at the end of its name for this call: function will add that by itself.
        """
        if action not in self.NEXT_TOKEN_OPERATIONS:
            raise MWSError(
                (
                    "{} action not listed in this API's NEXT_TOKEN_OPERATIONS. "
                    "Please refer to documentation."
                ).format(action)
            )

        action = "{}ByNextToken".format(action)

        data = dict(Action=action, NextToken=next_token)
        return self.make_request(data, method="POST")

    def calc_signature(self, method, request_description):
        """
        Calculate MWS signature to interface with Amazon

        Args:
            method (str)
            request_description (str)
        """
        sig_data = "\n".join(
            [
                method,
                self.domain.replace("https://", "").lower(),
                self.uri,
                request_description,
            ]
        )
        return base64.b64encode(
            hmac.new(
                self.secret_key.encode(), sig_data.encode(), hashlib.sha256
            ).digest()
        )

    def get_timestamp(self):
        """
        Returns the current timestamp in proper format.
        """
        return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
