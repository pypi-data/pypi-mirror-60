from amazon.account.actions import GetAmazonMarketplaceParticipations
from rest_framework.exceptions import ValidationError

from zonesmart.marketplace.exceptions import CreateChannelException
from zonesmart.marketplace.models import Domain, Marketplace
from zonesmart.marketplace.serializers.channel.base import BaseChannelSerializer


class CreateChannelSerializer(BaseChannelSerializer):
    class Meta(BaseChannelSerializer.Meta):
        read_only_fields = ["id"]

    def create(self, validated_data):
        marketplace_user_account = validated_data["marketplace_user_account"]
        # Check if marketplace is Amazon marketplace and validate available channel
        if marketplace_user_account.marketplace in Marketplace.amazon.all():
            api_action = GetAmazonMarketplaceParticipations(
                marketplace_user_account=marketplace_user_account
            )
            is_success, message, objects = api_action()
            if is_success:
                amazon_domain_code_list = [
                    marketplace["MarketplaceId"] for marketplace in objects["results"]
                ]
                available_domains = Domain.objects.filter(
                    marketplace=marketplace_user_account.marketplace,
                    code__in=amazon_domain_code_list,
                )
                if validated_data["domain"] not in available_domains:
                    raise ValidationError(
                        {
                            "domain": "Выбранный домен недоступен для добавления к выбранному аккаунту."
                        }
                    )
            else:
                raise CreateChannelException(
                    "Не удалось запросить список доступных для пользователя доменов Amazon."
                )
        return super().create(validated_data)
