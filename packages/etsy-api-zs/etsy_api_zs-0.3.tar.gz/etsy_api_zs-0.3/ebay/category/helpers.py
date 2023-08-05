from typing import Optional, Tuple

from django.core.cache import cache

from ebay.category import actions as category_actions
from ebay.category.models import EbayCategory
from ebay.listing import actions as listing_actions

from zonesmart.marketplace.models import MarketplaceUserAccount


def add_variation_supported_field_for_transport_aspects(
    aspects: list, category_id: str, marketplace_user_account: MarketplaceUserAccount
):
    # Call trading api for retrieve old aspects data
    trading_api_aspects_action = category_actions.GetTransportCategoryAspectsVS(
        marketplace_user_account=marketplace_user_account
    )
    is_success, message, objects = trading_api_aspects_action(category_id=category_id)
    if is_success:
        # Parse aspects for dictionary with aspect names and variation supported boolean
        objects = {
            item["Name"]: False
            if item["ValidationRules"].get("VariationSpecifics")
            else True
            for item in objects["results"]["Recommendations"]["NameRecommendation"]
        }
        # Add aspectEnabledForVariations for aspects
        for aspect in aspects:
            aspect["aspectConstraint"]["aspectEnabledForVariations"] = objects.get(
                aspect["localizedAspectName"], False
            )
    return is_success, message, aspects


def get_category_aspects(
    category: EbayCategory,
    marketplace_user_account: MarketplaceUserAccount = None,
    ignore_cache=False,
) -> Tuple[bool, str, Optional[dict]]:
    # Check if category is leaf
    if not category.is_leaf:
        return (
            False,
            "You can get aspects only for the leaf (is_leaf=True) category",
            None,
        )
    # Check cache for aspects
    cache_key = "aspects_" + str(category.id)
    is_success, message, aspects = (
        True,
        None,
        None if ignore_cache else cache.get(cache_key),
    )
    if is_success:
        message = "Aspects loaded successfully."
    if not aspects:
        api_action = category_actions.GetEbayCategoryAspects()
        # Get category aspects from transport support category
        category_tree_id = (
            "100"
            if category.transportSupported
            else category.category_tree.category_tree_id
        )
        category_id = category.category_id
        is_success, message, objects = api_action(
            category_id=category_id, category_tree_id=category_tree_id
        )
        if is_success:
            aspects = objects["results"]["aspects"]
            # Add variation supported field for EBAY_MOTORS_US aspects (it does not exists)
            if category_tree_id == "100":
                assert (
                    marketplace_user_account
                ), "marketplace_user_account should be specified for transport supported category."
                (
                    updated,
                    msg,
                    aspects,
                ) = add_variation_supported_field_for_transport_aspects(
                    aspects=aspects,
                    category_id=category_id,
                    marketplace_user_account=marketplace_user_account,
                )
                # Return error if retrieve is not successful
                if not updated:
                    return (
                        False,
                        "Не удалось получить данные о вариативных аспектах для транспортной категории. ",
                        None,
                    )
            # Skip cache save if skip_cache specified
            if not ignore_cache:
                cache.set(cache_key, aspects)
    return is_success, message, aspects


def get_properties(category: EbayCategory) -> Tuple[bool, str, Optional[list]]:
    # Get category & category id
    cache_key = "compatibility_properties_" + str(category.id)
    # Check cache
    is_success, message, property_list = True, None, cache.get(cache_key)
    # Get properties if not exists in cache
    if not property_list:
        api_action = listing_actions.GetProductCompatibilityProperties()
        is_success, message, objects = api_action(
            category_tree_id=category.category_tree.category_tree_id,
            category_id=category.category_id,
        )
        if is_success:
            property_list = objects["results"]
            # Cache properties for 1 day
            cache.set(cache_key, property_list)  # , timeout=86400)
    return is_success, message, property_list


def get_property_values(category: EbayCategory, name: str, filter_query: str):
    is_success, message, property_list = get_properties(category)
    # Create list of compatibility name and filter query names
    property_name_list = (
        [name]
        + [
            filter_query.split(":")[0]  # Get key (name) from K:V pair
            for filter_query in filter_query.split(",")  # Get list of K:V pairs
        ]
        if filter_query
        else [name]
    )
    # Check if compatibility property names in category property list
    # and raise an error if it does not exists
    available_property_name_list = [
        property_data["name"] for property_data in property_list
    ]
    if not all(name in available_property_name_list for name in property_name_list):
        error_name_list = ", ".join(
            name
            for name in property_name_list
            if name not in available_property_name_list
        )
        available_property_name_list = ", ".join(
            available_property["name"] for available_property in property_list
        )
        return (
            False,
            {
                "filter_query": (
                    f"Фильтр свойств содержит неподдерживаемые имена: {error_name_list}. "
                    f"Доступные имена свойств: {available_property_name_list}."
                )
            },
            None,
        )
    # Get property values
    api_action = listing_actions.GetCompatibilityPropertyValues()
    is_success, message, objects = api_action(
        category_tree_id=category.category_tree.category_tree_id,
        category_id=category.category_id,
        compatibility_property=name,
        filter_query=filter_query,
    )
    if is_success:
        objects = objects["results"]
    return is_success, message, objects
