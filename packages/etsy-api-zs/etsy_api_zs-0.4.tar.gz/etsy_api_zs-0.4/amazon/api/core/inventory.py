from .mws import MWS, utils


class Inventory(MWS):
    """
    Amazon MWS Inventory Fulfillment API
    """

    URI = "/FulfillmentInventory/2010-10-01"
    VERSION = "2010-10-01"
    NAMESPACE = "{http://mws.amazonaws.com/FulfillmentInventory/2010-10-01}"
    NEXT_TOKEN_OPERATIONS = [
        "ListInventorySupply",
    ]

    @utils.next_token_action("ListInventorySupply")
    def list_inventory_supply(
        self, skus=(), datetime_=None, response_group="Basic", next_token=None
    ):
        """
        Returns information on available inventory
        """

        data = dict(
            Action="ListInventorySupply",
            QueryStartDateTime=datetime_,
            ResponseGroup=response_group,
        )
        data.update(utils.enumerate_param("SellerSkus.member.", skus))
        return self.make_request(data, "POST")
