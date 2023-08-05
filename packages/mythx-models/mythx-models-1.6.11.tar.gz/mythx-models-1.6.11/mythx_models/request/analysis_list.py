"""This module contains the AnalysisListRequest domain model."""

from datetime import datetime
from typing import Any, Dict

import dateutil.parser

from mythx_models.exceptions import ValidationError
from mythx_models.request.base import BaseRequest

ANALYSIS_LIST_KEYS = ("offset", "dateFrom", "dateTo")


class AnalysisListRequest(BaseRequest):
    """Perform an API request that lists the logged in user's past analyses."""

    def __init__(
        self,
        offset: int,
        date_from: datetime,
        date_to: datetime,
        created_by: str,
        group_name: str,
    ):
        self.offset = offset
        self.date_from = date_from
        self.date_to = date_to
        self.created_by = created_by
        self.group_name = group_name

    @property
    def endpoint(self):
        """The API's analysis list endpoint.

        :return: A string denoting the list endpoint without the host prefix
        """
        return "v1/analyses"

    @property
    def method(self):
        """The HTTP method to perform.

        :return: The uppercase HTTP method, e.g. "POST"
        """
        return "GET"

    @property
    def headers(self):
        """Additional request headers.

        :return: A dict (str -> str) instance mapping header name to header content
        """
        return {}

    @property
    def parameters(self):
        """Additional URL parameters

        :return: A dict (str -> str) instance mapping parameter name to parameter content
        """
        return self.to_dict()

    @property
    def payload(self):
        """The request's payload data.

        :return: A Python dict to be serialized into JSON format and submitted to the endpoint.
        """
        return {}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        """Create the request domain model from a dict.

        This also validates the dict's schema and raises a :code:`ValidationError`
        if any required keys are missing or the data is malformed.

        :param d: The dict to deserialize from
        :return: The domain model with the data from :code:`d` filled in
        """
        if not all(k in d for k in ANALYSIS_LIST_KEYS):
            raise ValidationError(
                "Not all required keys {} found in data {}".format(
                    ANALYSIS_LIST_KEYS, d
                )
            )
        req = cls(
            offset=d["offset"],
            date_from=dateutil.parser.parse(d["dateFrom"]),
            date_to=dateutil.parser.parse(d["dateTo"]),
            created_by=d["createdBy"],
            group_name=d["groupName"],
        )

        return req

    def to_dict(self):
        """Serialize the request model to a Python dict.

        :return: A dict holding the request model data
        """
        return {
            "offset": self.offset,
            "dateFrom": self.date_from.isoformat() if self.date_from else None,
            "dateTo": self.date_from.isoformat() if self.date_from else None,
            "createdBy": self.created_by,
            "groupName": self.group_name,
        }

    def __eq__(self, other: "AnalysisListRequest"):
        return all(
            (
                self.offset == other.offset,
                self.date_from == other.date_from,
                self.date_to == other.date_to,
                self.created_by == other.created_by,
                self.group_name == other.group_name,
            )
        )
