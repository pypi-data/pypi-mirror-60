from ebay.listing.models import (
    EbayListing,
    EbayListingAspect,
    EbayProduct,
    EbayProductSpecification,
)
from ebay.listing.serializers.listing.remote_api.group import GroupSerializer
from ebay.listing.serializers.listing.remote_api.item import ItemSerializer
from ebay.listing.serializers.listing.remote_api.offer import OfferSerializer
from rest_framework import serializers

from zonesmart.serializers import ModelSerializerWithoutNullAndEmptyObjects


class EbayListingAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayListingAspect
        exclude = ["id", "listing"]

    def to_representation(self, instance):
        return instance.name, instance.value


class EbayListingSerializer(ModelSerializerWithoutNullAndEmptyObjects):
    class Meta:
        model = EbayListing
        fields = "__all__"

    def to_representation(self, instance: EbayListing):
        # Create listing aspects representation
        listing_aspects = instance.aspects.all()
        listing_aspects_representation = dict()
        # If aspects exists
        if listing_aspects.exists():
            listing_aspects_data = EbayListingAspectSerializer(
                instance=instance.aspects.all(), many=True
            ).data
            # Parse aspects for duplicated keys and represent as list of values with unique names
            listing_aspects_representation = dict()
            for data in listing_aspects_data:
                name, value = data
                if name not in listing_aspects_representation:
                    listing_aspects_representation[name] = [value]
                else:
                    listing_aspects_representation[name].append(value)
        #
        title = instance.title
        locale = instance.localizedFor
        marketplace_id = instance.channel.domain.code
        category_id = instance.category.category_id
        #
        product_qs = instance.products.all()
        # Get items for representation
        items = ItemSerializer(
            instance=product_qs,
            listing_aspects_representation=listing_aspects_representation,
            title=title,
            locale=locale,
            many=True,
        ).data
        # Get offers for representation
        listing_polices_representation = {
            "fulfillmentPolicyId": instance.fulfillmentPolicy.policy_id,
            "returnPolicyId": instance.returnPolicy.policy_id,
            "paymentPolicyId": instance.paymentPolicy.policy_id,
        }
        offers = OfferSerializer(
            instance=product_qs,
            marketplace_id=marketplace_id,
            category_id=category_id,
            listing_polices_representation=listing_polices_representation,
            listing_description=instance.listing_description,
            merchant_location_key=instance.location.merchantLocationKey,
            many=True,
        ).data
        # Create final representation
        representation = {"items": {"requests": items}, "offers": {"requests": offers}}
        if product_qs.count() > 1:
            group_data = GroupSerializer(instance=instance).data
            group_data["aspects"] = listing_aspects_representation
            image_urls = [url for item in items for url in item["product"]["imageUrls"]]
            group_data["imageUrls"] = image_urls
            representation["group"] = {
                "create": group_data,
                "publish": {
                    "inventoryItemGroupKey": group_data["inventoryItemGroupKey"],
                    "marketplaceId": marketplace_id,
                },
            }
        # Return representation
        return self.clean_representation(representation)


class DownloadEbayListingAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayListingAspect
        exclude = ["id", "listing"]


class DownloadEbayProductSpecificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProductSpecification
        exclude = ["id", "product"]


class DownloadEbayProductSerializer(serializers.ModelSerializer):
    specifications = DownloadEbayProductSpecificationsSerializer(many=True)

    class Meta:
        model = EbayProduct
        exclude = ["id", "listing"]


class DownloadEbayListingSerializer(serializers.ModelSerializer):
    products = DownloadEbayProductSerializer(many=True)
    aspects = DownloadEbayListingAspectSerializer(many=True)

    class Meta:
        model = EbayListing
        fields = [
            "listing_description",
            "listing_sku",
            "groupListingId",
            "products",
            "title",
            "paymentPolicy",
            "returnPolicy",
            "fulfillmentPolicy",
            "location",
            "aspects",
        ]

    def create(self, validated_data):
        listing_sku = validated_data.pop("listing_sku")
        channel = validated_data.pop("channel")
        group_listing_id = validated_data.pop("groupListingId")
        instance, updated = self.Meta.model.objects.update_or_create(
            listing_sku=listing_sku,
            channel=channel,
            groupListingId=group_listing_id,
            defaults=validated_data,
        )
        instance.status = "published"
        instance.save()
        return instance
