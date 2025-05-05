from django import forms

class SearchForm(forms.Form):
    subreddit = forms.CharField(label="subreddit", max_length=200)
    key_word = forms.CharField(label="key_word", max_length=100)
