from .mws import MWS, utils


class Reports(MWS):
    """
    Amazon MWS Reports API
    """

    ACCOUNT_TYPE = "Merchant"
    NEXT_TOKEN_OPERATIONS = [
        "GetReportRequestList",
        "GetReportList",
        "GetReportScheduleList",
    ]

    # * REPORTS * #

    def get_report(self, report_id):
        data = dict(Action="GetReport", ReportId=report_id)
        return self.make_request(data)

    def get_report_count(
        self, report_types=(), acknowledged=None, from_date=None, to_date=None
    ):
        data = dict(
            Action="GetReportCount",
            Acknowledged=acknowledged,
            AvailableFromDate=from_date,
            AvailableToDate=to_date,
        )
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        return self.make_request(data)

    @utils.next_token_action("GetReportList")
    def get_report_list(
        self,
        request_ids=(),
        max_count=None,
        report_types=(),
        acknowledged=None,
        from_date=None,
        to_date=None,
        next_token=None,
    ):
        data = dict(
            Action="GetReportList",
            Acknowledged=acknowledged,
            AvailableFromDate=from_date,
            AvailableToDate=to_date,
            MaxCount=max_count,
        )
        data.update(utils.enumerate_param("ReportRequestIdList.Id.", request_ids))
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        return self.make_request(data)

    def get_report_request_count(
        self, report_types=(), processing_statuses=(), from_date=None, to_date=None
    ):
        data = dict(
            Action="GetReportRequestCount",
            RequestedFromDate=from_date,
            RequestedToDate=to_date,
        )
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        data.update(
            utils.enumerate_param(
                "ReportProcessingStatusList.Status.", processing_statuses
            )
        )
        return self.make_request(data)

    @utils.next_token_action("GetReportRequestList")
    def get_report_request_list(
        self,
        request_ids=(),
        report_types=(),
        processing_statuses=(),
        max_count=None,
        from_date=None,
        to_date=None,
        next_token=None,
    ):
        data = dict(
            Action="GetReportRequestList",
            MaxCount=max_count,
            RequestedFromDate=from_date,
            RequestedToDate=to_date,
        )
        data.update(utils.enumerate_param("ReportRequestIdList.Id.", request_ids))
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        data.update(
            utils.enumerate_param(
                "ReportProcessingStatusList.Status.", processing_statuses
            )
        )
        return self.make_request(data)

    def request_report(
        self, report_type, start_date=None, end_date=None, marketplaceids=(), **kwargs
    ):
        data = dict(
            Action="RequestReport",
            ReportType=report_type,
            StartDate=start_date,
            EndDate=end_date,
        )
        data.update(utils.enumerate_param("MarketplaceIdList.Id.", marketplaceids))

        # Browse Tree Report extra options
        if report_type == "_GET_XML_BROWSE_TREE_DATA_":
            # Example: 'ReportOptions=MarketplaceId%3DATVPDKIKX0DER;BrowseNodeId%3D15706661'
            ReportOptions = ";".join(
                [
                    f"{param}={kwargs[param]}"
                    for param in ["MarketplaceId", "RootNodesOnly", "BrowseNodeId"]
                    if param in kwargs
                ]
            )
            data.update({"ReportOptions": ReportOptions})

        return self.make_request(data)

    # * ReportSchedule * #

    def get_report_schedule_list(self, report_types=()):
        data = dict(Action="GetReportScheduleList")
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        return self.make_request(data)

    def get_report_schedule_count(self, report_types=()):
        data = dict(Action="GetReportScheduleCount")
        data.update(utils.enumerate_param("ReportTypeList.Type.", report_types))
        return self.make_request(data)
