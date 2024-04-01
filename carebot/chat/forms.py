from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={'id': 'user-query', 'rows': '1', 'class': 'form-control', 'placeholder': 'Type your query here...', 'autocomplete': 'off', 'autofocus': 'true', 'spellcheck': 'on', 'wrap': 'soft', 'maxlength': '1000'})
    )
