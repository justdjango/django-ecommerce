from __future__ import absolute_import, division, print_function

from stripe.stripe_object import StripeObject


class CreditNoteLineItem(StripeObject):
    OBJECT_NAME = "credit_note_line_item"
