from __future__ import absolute_import, division, print_function

from stripe import api_requestor
from stripe import util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import custom_method


@custom_method("void_credit_note", http_verb="post", http_path="void")
class CreditNote(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):
    OBJECT_NAME = "credit_note"

    def void_credit_note(self, idempotency_key=None, **params):
        url = self.instance_url() + "/void"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(self.request("post", url, params, headers))
        return self

    @classmethod
    def preview(
        cls, api_key=None, stripe_version=None, stripe_account=None, **params
    ):
        requestor = api_requestor.APIRequestor(
            api_key, api_version=stripe_version, account=stripe_account
        )
        url = cls.class_url() + "/preview"
        response, api_key = requestor.request("get", url, params)
        return util.convert_to_stripe_object(
            response, api_key, stripe_version, stripe_account
        )
