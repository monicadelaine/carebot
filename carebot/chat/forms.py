from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type your query here...'})
    )
