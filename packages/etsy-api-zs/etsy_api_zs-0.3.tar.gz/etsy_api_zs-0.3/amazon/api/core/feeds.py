from .mws import MWS, calc_md5, utils


class Feeds(MWS):
    """
    Amazon MWS Feeds API
    """

    ACCOUNT_TYPE = "Merchant"

    NEXT_TOKEN_OPERATIONS = [
        "GetFeedSubmissionList",
    ]

    def submit_feed(
        self,
        feed,
        feed_type,
        marketplace_ids=None,
        content_type="text/xml",
        purge="false",
    ):
        """
        Uploads a feed ( xml or .tsv ) to the seller's inventory.
        Can be used for creating/updating products on Amazon.
        """
        data = dict(Action="SubmitFeed", FeedType=feed_type, PurgeAndReplace=purge)
        data.update(utils.enumerate_param("MarketplaceIdList.Id.", marketplace_ids))
        md = calc_md5(feed)
        return self.make_request(
            data,
            method="POST",
            body=feed,
            extra_headers={"Content-MD5": md, "Content-Type": content_type},
        )

    @utils.next_token_action("GetFeedSubmissionList")
    def get_feed_submission_list(
        self,
        feed_ids=None,
        max_count=None,
        feed_types=None,
        processing_status=None,
        from_date=None,
        to_date=None,
        next_token=None,
    ):
        """
        Returns a list of all feed submissions submitted in the previous 90 days.
        That match the query parameters.
        """

        data = dict(
            Action="GetFeedSubmissionList",
            MaxCount=max_count,
            SubmittedFromDate=from_date,
            SubmittedToDate=to_date,
        )
        data.update(utils.enumerate_param("FeedSubmissionIdList.Id", feed_ids))
        data.update(utils.enumerate_param("FeedTypeList.Type.", feed_types))
        data.update(
            utils.enumerate_param("FeedProcessingStatusList.Status.", processing_status)
        )
        return self.make_request(data)

    def get_feed_submission_count(
        self, feed_types=None, processing_status=None, from_date=None, to_date=None
    ):
        data = dict(
            Action="GetFeedSubmissionCount",
            SubmittedFromDate=from_date,
            SubmittedToDate=to_date,
        )
        data.update(utils.enumerate_param("FeedTypeList.Type.", feed_types))
        data.update(
            utils.enumerate_param("FeedProcessingStatusList.Status.", processing_status)
        )
        return self.make_request(data)

    def cancel_feed_submissions(
        self, feed_ids=None, feed_types=None, from_date=None, to_date=None
    ):
        data = dict(
            Action="CancelFeedSubmissions",
            SubmittedFromDate=from_date,
            SubmittedToDate=to_date,
        )
        data.update(utils.enumerate_param("FeedSubmissionIdList.Id.", feed_ids))
        data.update(utils.enumerate_param("FeedTypeList.Type.", feed_types))
        return self.make_request(data)

    def get_feed_submission_result(self, feed_id):
        data = dict(Action="GetFeedSubmissionResult", FeedSubmissionId=feed_id)
        return self.make_request(data, rootkey="Message")
