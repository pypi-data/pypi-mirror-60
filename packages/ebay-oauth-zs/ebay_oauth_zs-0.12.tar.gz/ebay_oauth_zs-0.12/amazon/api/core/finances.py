from .mws import MWS, utils


class Finances(MWS):
    """
    Amazon MWS Finances API
    """

    URI = "/Finances/2015-05-01"
    VERSION = "2015-05-01"
    NS = "{https://mws.amazonservices.com/Finances/2015-05-01}"
    NEXT_TOKEN_OPERATIONS = [
        "ListFinancialEventGroups",
        "ListFinancialEvents",
    ]

    @utils.next_token_action("ListFinancialEventGroups")
    def list_financial_event_groups(
        self, created_after=None, created_before=None, max_results=None, next_token=None
    ):
        """
        Returns a list of financial event groups
        """
        data = dict(
            Action="ListFinancialEventGroups",
            FinancialEventGroupStartedAfter=created_after,
            FinancialEventGroupStartedBefore=created_before,
            MaxResultsPerPage=max_results,
        )
        return self.make_request(data)

    @utils.next_token_action("ListFinancialEvents")
    def list_financial_events(
        self,
        financial_event_group_id=None,
        amazon_order_id=None,
        posted_after=None,
        posted_before=None,
        max_results=None,
        next_token=None,
    ):
        """
        Returns financial events for a user-provided FinancialEventGroupId or AmazonOrderId
        """
        data = dict(
            Action="ListFinancialEvents",
            FinancialEventGroupId=financial_event_group_id,
            AmazonOrderId=amazon_order_id,
            PostedAfter=posted_after,
            PostedBefore=posted_before,
            MaxResultsPerPage=max_results,
        )
        return self.make_request(data)
