from django import forms

from .models import Comment, Record


class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к записям
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'rows': 5, 'cols': 1, 'placeholder': 'Комментарий', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ('content',)


class RecordCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """
    class Meta:
        model = Record
        fields = ('title', 'slug', 'short_description', 'full_description', 'thumbnail', 'status', 'tags_places', 'tags_people')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

        self.fields['short_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['short_description'].required = False
        self.fields['full_description'].required = False


class RecordUpdateForm(RecordCreateForm):
    """
    Форма обновления записи на сайте
    """
    class Meta:
        model = Record
        fields = RecordCreateForm.Meta.fields + ('updater',)

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)

        self.fields['short_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['short_description'].required = False
        self.fields['full_description'].required = False
