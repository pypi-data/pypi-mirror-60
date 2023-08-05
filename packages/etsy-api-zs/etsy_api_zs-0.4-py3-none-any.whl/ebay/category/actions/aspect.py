from ebay.api.ebay_action import EbayAction
from ebay_api.commerce.taxonomy import GetItemAspectsForCategory
from ebay_api.sell.metadata.marketplace import GetItemConditionPolicies


class GetEbayCategoryAspects(EbayAction):
    description = "Получение аспектов для категории товаров eBay"
    api_class = GetItemAspectsForCategory


class GetEbayProductConditions(EbayAction):
    description = "Получение допустимых состояний товара eBay"
    api_class = GetItemConditionPolicies
