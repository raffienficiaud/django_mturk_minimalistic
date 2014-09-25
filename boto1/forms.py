# -*- coding: utf-8 -*-
from django import forms

class FormAMT(forms.Form):
    document = forms.CharField(
      widget = forms.Textarea,
      help_text='annotate the image, and do it well'
    )
    image = forms.CharField()

    # the forms will contain the assignment ID that will be sent back to Amazon
    assignmentId = forms.CharField(widget = forms.HiddenInput)
