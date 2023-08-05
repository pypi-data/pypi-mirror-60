from etsy.api.etsy_action import EtsyAction
from etsy.serializers.remote.download import (
    DownloadEtsyCountrySerializer,
    DownloadEtsyRegionSerializer,
)


class GetEtsyCountries(EtsyAction):
    api_method = "findAllCountry"


class DownloadEtsyCountries(GetEtsyCountries):
    def success_trigger(self, message, objects, **kwargs):
        serializer = DownloadEtsyCountrySerializer(data=objects["results"], many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().success_trigger(message, objects, **kwargs)


class GetEtsyRegions(EtsyAction):
    api_method = "findEligibleRegions"


class DownloadEtsyRegions(GetEtsyRegions):
    def success_trigger(self, message, objects, **kwargs):
        serializer = DownloadEtsyRegionSerializer(data=objects["results"], many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().success_trigger(message, objects, **kwargs)
