from django import forms
import pandas as pd

ANSWERS = (('', '-'),('yes', 'Yes'), ('no', 'No'))

CLASSES = (('', '-'), ('1', '1'), ('2', '2'), ('3', '3'),('4','4'),('5','5'),('6','6'),('7','7'),
            ('8','8'),('9','9'),('10','10'),('11','12'),('13','13'),('14','14'),('15','15'),('16','16'),
            ('17','17'),('18','18'),('19','19'),('20','20'))


class FeedbackForm(forms.Form):
    class_per_week = forms.ChoiceField(choices=CLASSES)
    instructor = forms.ChoiceField(choices=ANSWERS)
    duration = forms.ChoiceField(choices=ANSWERS)
    timetable = forms.ChoiceField(choices=ANSWERS)
    class_size = forms.ChoiceField(choices=ANSWERS)
    facilities = forms.ChoiceField(choices=ANSWERS)
    price = forms.ChoiceField(choices=ANSWERS)