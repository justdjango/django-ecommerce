from __future__ import absolute_import, division, print_function

from stripe.api_resources.abstract import ListableAPIResource


class IssuerFraudRecord(ListableAPIResource):
    OBJECT_NAME = "issuer_fraud_record"
