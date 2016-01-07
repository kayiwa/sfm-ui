from django import forms
from .models import Collection, SeedSet, Seed, Credential
import json
from .widgets import MultiWidgetLayout


class CollectionForm(forms.ModelForm):

    class Meta:
        model = Collection
        fields = '__all__'
        exclude = []
        widgets = None
        localized_fields = None
        labels = {}
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        return super(CollectionForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        return super(CollectionForm, self).is_valid()

    def full_clean(self):
        return super(CollectionForm, self).full_clean()

    def save(self, commit=True):
        return super(CollectionForm, self).save(commit)


class SeedSetForm(forms.ModelForm):

    OPTIONS = (
        ('daily', 'daily'),
        ('hourly', 'hourly'),
        ('minutely', 'minutely'),
    )

    schedule = forms.CharField(max_length=12,
                               widget=forms.Select(choices=OPTIONS))
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = SeedSet
        fields = '__all__'
        exclude = []
        widgets = {}
        localized_fields = None
        labels = {}
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        return super(SeedSetForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        return super(SeedSetForm, self).is_valid()

    def full_clean(self):
        return super(SeedSetForm, self).full_clean()

    def save(self, commit=True):
        return super(SeedSetForm, self).save(commit)


class SeedForm(forms.ModelForm):

    class Meta:
        model = Seed
        fields = ["seed_set", "token", "uid", "is_active"]
        exclude = []
        widgets = None
        localized_fields = None
        labels = {}
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        return super(SeedForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        return super(SeedForm, self).is_valid()

    def full_clean(self):
        return super(SeedForm, self).full_clean()

    def save(self, commit=True):
        return super(SeedForm, self).save(commit)


class TwitterFilterWidget(MultiWidgetLayout):
    # See http://tothinkornottothink.com/post/10815277049/django-forms-i-custom-fields-and-widgets-in
    def __init__(self, attrs=None):
            layout = [
                "<label for='%(id)s'>Follow:</label>", forms.TextInput(),
                "<label for='%(id)s'>Track:</label>", forms.TextInput()
            ]
            super(TwitterFilterWidget, self).__init__(layout, attrs)

    def decompress(self, value):
        if value:
            return json.loads(value)
        else:
            return ["", ""]


class TwitterFilterField(forms.fields.MultiValueField):
    widget = TwitterFilterWidget

    def __init__(self, *args, **kwargs):
        list_fields = [forms.fields.CharField(),
                       forms.fields.CharField()]
        super(TwitterFilterField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return json.dumps(values)


class TwitterFilterForm(SeedForm):
    token = TwitterFilterField(label="Token")


class CredentialForm(forms.ModelForm):

    class Meta:
        model = Credential
        fields = '__all__'
        exclude = []
        widgets = None
        localized_fields = None
        labels = {}
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        return super(CredentialForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        return super(CredentialForm, self).is_valid()

    def full_clean(self):
        return super(CredentialForm, self).full_clean()

    def save(self, commit=True):
        return super(CredentialForm, self).save(commit)


