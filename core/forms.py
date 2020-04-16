from django import forms
import pandas as pd

ANSWERS = (('', '-'), ('Yes', 'Yes'), ('No', 'No'))

CLASSES = (('', '-'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
            ('8', '8'), ('9', '9'), ('10', '10'), ('11', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'),
            ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'))

IMPORTANCE = (('', '-'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))


class FeedbackForm(forms.Form):
    Classes_per_week = forms.ChoiceField(choices=CLASSES)
    Happy_with_instructors = forms.ChoiceField(choices=ANSWERS)
    Happy_with_class_duration = forms.ChoiceField(choices=ANSWERS)
    Happy_with_class_timings = forms.ChoiceField(choices=ANSWERS)
    Happy_with_class_size = forms.ChoiceField(choices=ANSWERS)
    Happy_with_facilities = forms.ChoiceField(choices=ANSWERS)
    Happy_with_price = forms.ChoiceField(choices=ANSWERS)


class NewUserForm(forms.Form):
    Lose_weight = forms.ChoiceField(choices=IMPORTANCE)
    Stay_fit = forms.ChoiceField(choices=IMPORTANCE)
    Build_muscle = forms.ChoiceField(choices=IMPORTANCE)
    Stretching = forms.ChoiceField(choices=IMPORTANCE)
