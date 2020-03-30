from django import forms
import pandas as pd

ANSWERS = (('', '-'),('yes', 'Yes'), ('no', 'No'))

INSTRUCTOR = (('', '-'), ('1', '1'), ('2', '2'), ('3', '3'))


class FeedbackForm(forms.Form):
    class_per_week = forms.ChoiceField(choices=INSTRUCTOR)
    timetable = forms.ChoiceField(choices=ANSWERS)
    instructor = forms.ChoiceField(choices=ANSWERS)
    capacity = forms.ChoiceField(choices=ANSWERS)
    duration = forms.ChoiceField(choices=ANSWERS)
    class_size = forms.ChoiceField(choices=ANSWERS)
    facilities = forms.ChoiceField(choices=ANSWERS)
    price = forms.ChoiceField(choices=ANSWERS)