from __future__ import absolute_import, division, print_function

from stripe.util import merge_dicts
from stripe.stripe_object import StripeObject


class ErrorObject(StripeObject):
    def refresh_from(
        self,
        values,
        api_key=None,
        partial=False,
        stripe_version=None,
        stripe_account=None,
        last_response=None,
    ):
        # Unlike most other API resources, the API will omit attributes in
        # error objects when they have a null value. We manually set default
        # values here to facilitate generic error handling.
        values = merge_dicts(
            {
                "charge": None,
                "code": None,
                "decline_code": None,
                "doc_url": None,
                "message": None,
                "param": None,
                "payment_intent": None,
                "payment_method": None,
                "setup_intent": None,
                "source": None,
                "type": None,
            },
            values,
        )
        return super(ErrorObject, self).refresh_from(
            values,
            api_key,
            partial,
            stripe_version,
            stripe_account,
            last_response,
        )


class OAuthErrorObject(StripeObject):
    def refresh_from(
        self,
        values,
        api_key=None,
        partial=False,
        stripe_version=None,
        stripe_account=None,
        last_response=None,
    ):
        # Unlike most other API resources, the API will omit attributes in
        # error objects when they have a null value. We manually set default
        # values here to facilitate generic error handling.
        values = merge_dicts(
            {"error": None, "error_description": None}, values
        )
        return super(OAuthErrorObject, self).refresh_from(
            values,
            api_key,
            partial,
            stripe_version,
            stripe_account,
            last_response,
        )
