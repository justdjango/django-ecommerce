from django import forms
import pandas as pd

ANSWERS = (('', '-'),('yes', 'Yes'), ('no', 'No'))


class FeedbackForm(forms.Form):
    timetable = forms.ChoiceField(choices=ANSWERS)
    capacity = forms.ChoiceField(choices=ANSWERS)
    duration = forms.ChoiceField(choices=ANSWERS)
    facilities = forms.ChoiceField(choices=ANSWERS)
    price = forms.ChoiceField(choices=ANSWERS)