from amazon.order.serializers.order.base import BaseAmazonOrderSerializer


class CreateAmazonOrderSerializer(BaseAmazonOrderSerializer):
    class Meta(BaseAmazonOrderSerializer.Meta):
        pass
