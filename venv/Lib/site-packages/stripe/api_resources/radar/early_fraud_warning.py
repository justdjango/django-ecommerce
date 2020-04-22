from __future__ import absolute_import, division, print_function

from stripe.api_resources.abstract import ListableAPIResource


class EarlyFraudWarning(ListableAPIResource):
    OBJECT_NAME = "radar.early_fraud_warning"
