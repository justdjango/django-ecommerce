from __future__ import absolute_import, division, print_function

from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource


class Transaction(ListableAPIResource, UpdateableAPIResource):
    OBJECT_NAME = "issuing.transaction"
