from __future__ import absolute_import, division, print_function

from stripe.api_resources.abstract import ListableAPIResource


class BalanceTransaction(ListableAPIResource):
    OBJECT_NAME = "balance_transaction"
