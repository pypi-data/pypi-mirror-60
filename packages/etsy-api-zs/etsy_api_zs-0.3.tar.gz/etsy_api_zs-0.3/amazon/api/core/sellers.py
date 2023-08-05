from .mws import MWS, utils


class Sellers(MWS):
    """
    Amazon MWS Sellers API
    """

    URI = "/Sellers/2011-07-01"
    VERSION = "2011-07-01"
    NAMESPACE = "{http://mws.amazonservices.com/schema/Sellers/2011-07-01}"
    NEXT_TOKEN_OPERATIONS = [
        "ListMarketplaceParticipations",
    ]

    @utils.next_token_action("ListMarketplaceParticipations")
    def list_marketplace_participations(self, next_token=None):
        """
        Returns a list of marketplaces a seller can participate in and
        a list of participations that include seller-specific information in that marketplace.
        The operation returns only those marketplaces where the seller's account is
        in an active state.

        Run with `next_token` kwarg to call related "ByNextToken" action.
        """
        data = dict(Action="ListMarketplaceParticipations")
        return self.make_request(data)
