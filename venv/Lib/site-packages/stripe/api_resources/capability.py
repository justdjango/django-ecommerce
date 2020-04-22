from __future__ import absolute_import, division, print_function

from stripe import util
from stripe.api_resources.account import Account
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.six.moves.urllib.parse import quote_plus


class Capability(UpdateableAPIResource):
    OBJECT_NAME = "capability"

    def instance_url(self):
        token = util.utf8(self.id)
        account = util.utf8(self.account)
        base = Account.class_url()
        acct_extn = quote_plus(account)
        extn = quote_plus(token)
        return "%s/%s/capabilities/%s" % (base, acct_extn, extn)

    @classmethod
    def modify(cls, sid, **params):
        raise NotImplementedError(
            "Can't update a capability without an account ID. Update a capability using "
            "account.modify_capability('acct_123', 'acap_123', params)"
        )

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        raise NotImplementedError(
            "Can't retrieve a capability without an account ID. Retrieve a capability using "
            "account.retrieve_capability('acct_123', 'acap_123')"
        )
