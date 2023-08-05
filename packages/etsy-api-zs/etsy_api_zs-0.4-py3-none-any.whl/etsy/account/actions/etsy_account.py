from etsy.account.models import EtsyUserAccountInfo
from etsy.account.serializers import EtsyUserAccountInfoSerializer
from etsy.api.etsy_action import EtsyAccountAction


class GetEtsyUserAccountInfo(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/user#method_getuser
    """

    api_method = "getUser"
    params = ["user_id"]


class DownloadEtsyUserAccountInfo(GetEtsyUserAccountInfo):
    def success_trigger(self, message, objects, **kwargs):
        if kwargs["user_id"] != "__SELF__":
            is_success = False
            message = "Нельзя сохранить информацию о другом пользователе"
        else:
            if objects["count"] != 1:
                is_success = False
                message = "Аккаунт не найден."
            else:
                serializer = EtsyUserAccountInfoSerializer(data=objects["results"][0])
                etsy_account = self.marketplace_user_account.marketplace_account
                try:
                    instance = EtsyUserAccountInfo.objects.get(
                        etsy_account=etsy_account
                    )
                except EtsyUserAccountInfo.DoesNotExist:
                    pass
                else:
                    serializer.instance = instance

                if serializer.is_valid():
                    serializer.save(etsy_account=etsy_account)
                    is_success = True
                else:
                    is_success = False
                    message = str(serializer.errors)
                    objects["errors"] = serializer.errors
        return is_success, message, objects
