import logging
from time import sleep

# from django.conf import settings
from django.test import TestCase
from django.utils.http import urlencode

import factory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class BaseTest(TestCase):
    fixtures = [
        "group",
        "user",
        "marketplace",
        "domain",
    ]

    def setUp(self):
        logging.disable(logging.CRITICAL)
        # settings.EBAY_SANDBOX = False
        self.email = "admin@zonesmart.ru"
        self.password = "4815162342"

    @property
    def api_headers(self):
        return {
            "HTTP_AUTHORIZATION": f"JWT {self.access_token}",
        }

    def get_jwt_tokens(self, email, password):
        data = {
            "email": email,
            "password": password,
        }
        return self.make_request(
            method="POST", url_path="/api/auth/jwt/create/", data=data, auth=False
        )

    def refresh_jwt_access_token(self, refresh_token):
        data = {"refresh": refresh_token}
        return self.make_request(
            method="POST", url_path="/api/auth/jwt/refresh/", data=data, auth=False
        )

    def verify_jwt_access_token(self, access_token):
        data = {"token": access_token}
        return self.make_request(
            method="POST", url_path="/api/auth/jwt/verify/", data=data, auth=False
        )

    def update_jwt_token(self):
        response = self.get_jwt_tokens(email=self.email, password=self.password)
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            self.access_token = response.json()["access"]
            self.refresh_token = response.json()["refresh"]

    def make_request(
        self,
        method: str,
        url_path: str,
        data=None,
        data_format: str = "json",
        auth: bool = True,
    ):
        if data is None:
            data = dict()

        client = APIClient(enforce_csrf_checks=True)
        if auth:
            self.update_jwt_token()
            client.credentials(HTTP_AUTHORIZATION=f"JWT {self.access_token}")

        method = method.upper()
        if method == "POST":
            request_method = client.post
        elif method == "GET":
            request_method = client.get
        elif method == "DELETE":
            request_method = client.delete
        elif method == "PUT":
            request_method = client.put
        elif method == "PATCH":
            request_method = client.patch
        else:
            raise AttributeError(f"Недопустимый метод: {method}")

        response = request_method(path=url_path, data=data, format=data_format,)

        return response

    def assertStatus(self, response, status=status.HTTP_200_OK):
        self.assertEqual(response.status_code, status)

    def obj_factory_to_dict(self, obj_factory, clean=True):
        obj_dict = factory.build(dict, FACTORY_CLASS=obj_factory)
        if clean:
            for key, value in list(obj_dict.items()):
                if not isinstance(value, str):
                    if hasattr(value, "id"):
                        obj_dict[key] = str(value.id)
                    elif callable(value):
                        obj_dict[key] = str(value())
                    else:
                        obj_dict.pop(key)
        return obj_dict


class BaseAPIViewTest(BaseTest):
    url_path = None

    def __init__(self, *args, **kwargs):
        assert self.url_path, "url_path parameter not specified"
        super().__init__(*args, **kwargs)

    def get_url(self, **kwargs) -> str:
        url = reverse(self.url_path, kwargs=kwargs)
        return url


class BaseViewSetTest(BaseAPIViewTest):
    def get_url(self, postfix: str = "detail", query_params=None, **kwargs) -> str:
        if query_params is None:
            query_params = {}

        url = reverse(f"{self.url_path}-{postfix}", kwargs=kwargs)
        if query_params:
            url += "?" + urlencode(query_params)

        return url


class BaseActionTest(BaseTest):
    def perform_action(
        self,
        action=None,
        action_class=None,
        assert_success: bool = True,
        retry_if_500=False,
        retries_num: int = 3,
        **kwargs,
    ):
        if bool(action) == bool(action_class):
            raise AttributeError("Необходимо задать либо action, либо action_class")
        elif action_class:
            action = action_class(
                channel=kwargs.pop("channel", None),
                marketplace_user_account=kwargs.pop("marketplace_user_account", None),
                entity=kwargs.pop("entity", None),
            )

        if retry_if_500:
            for _ in range(retries_num):
                is_success, message, objects = action(**kwargs)
                if not is_success:
                    if "response" in objects:
                        if str(
                            getattr(objects["response"], "status_code", "")
                        ).startswith("5"):
                            sleep(3)
                            continue
                break
        else:
            is_success, message, objects = action(**kwargs)

        if assert_success:
            self.assertTrue(is_success, message)
        else:
            self.assertFalse(is_success, message)
        return is_success, message, objects


class BaseSeleniumTest(BaseTest):
    def get_selenium_driver(self):
        try:
            import selenium

            self.driver = selenium.webdriver.Remote(
                command_executor="http://hub:4444/wd/hub",
                desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            )
        except ImportError:
            raise ImportError(
                "selenium module not found, try to run test.yml compose instead of local.yml"
            )
