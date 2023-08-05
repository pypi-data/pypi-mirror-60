# Available detail names: https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/DetailNameCodeType.html
from ebay.api.ebay_trading_api_action import EbayTradingAPIAction


class GetEbayDetails(EbayTradingAPIAction):
    detail_name = None
    verb = "GeteBayDetails"

    def get_params(self, detail_names: list = None, **kwargs):
        if not detail_names:
            if self.detail_name:
                detail_names = self.detail_name
            else:
                raise AttributeError(f'Необходимо задать параметр "detail_names"')

        return {"DetailName": detail_names}

    def success_trigger(self, message, objects, **kwargs):
        if self.detail_name:
            objects["results"] = objects["results"].get(self.detail_name, [])
        return super().success_trigger(message, objects, **kwargs)


class GetEbayDispatchTimeMaxDetails(GetEbayDetails):
    detail_name = "DispatchTimeMaxDetails"


class GetEbayRegionOfOriginDetails(GetEbayDetails):
    detail_name = "RegionOfOriginDetails"


class GetEbayRegionDetails(GetEbayDetails):
    detail_name = "RegionDetails"
