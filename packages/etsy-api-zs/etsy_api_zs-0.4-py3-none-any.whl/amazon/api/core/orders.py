from .mws import MWS, utils


class OrdersError(Exception):
    pass


class Orders(MWS):
    """
    Amazon Orders API
    """

    URI = "/Orders/2013-09-01"
    VERSION = "2013-09-01"
    NAMESPACE = "{https://mws.amazonservices.com/Orders/2013-09-01}"
    NEXT_TOKEN_OPERATIONS = [
        "ListOrders",
        "ListOrderItems",
    ]

    @utils.next_token_action("ListOrders")
    def list_orders(
        self,
        marketplace_ids: list,
        created_after=None,
        created_before=None,
        lastupdatedafter=None,
        lastupdatedbefore=None,
        orderstatus=(),
        fulfillment_channels=(),
        payment_methods=(),
        buyer_email=None,
        seller_orderid=None,
        max_results="100",
        next_token=None,
    ):

        if bool(created_after) == bool(lastupdatedafter):
            raise OrdersError(
                "Необходимо задать значение либо created_after, либо last_updated_after."
            )

        data = dict(
            Action="ListOrders",
            CreatedAfter=created_after,
            CreatedBefore=created_before,
            LastUpdatedAfter=lastupdatedafter,
            LastUpdatedBefore=lastupdatedbefore,
            BuyerEmail=buyer_email,
            SellerOrderId=seller_orderid,
            MaxResultsPerPage=max_results,
        )
        data.update(utils.enumerate_param("OrderStatus.Status.", orderstatus))
        data.update(utils.enumerate_param("MarketplaceId.Id.", marketplace_ids))
        data.update(
            utils.enumerate_param("FulfillmentChannel.channel.", fulfillment_channels)
        )
        data.update(utils.enumerate_param("PaymentMethod.Method.", payment_methods))
        return self.make_request(data)

    def get_orders(self, amazon_order_ids):
        data = dict(Action="GetOrder")
        data.update(utils.enumerate_param("AmazonOrderId.Id.", amazon_order_ids))
        return self.make_request(data)

    @utils.next_token_action("ListOrderItems")
    def list_order_items(self, amazon_order_id, next_token=None):
        data = dict(Action="ListOrderItems", AmazonOrderId=amazon_order_id)
        return self.make_request(data)
