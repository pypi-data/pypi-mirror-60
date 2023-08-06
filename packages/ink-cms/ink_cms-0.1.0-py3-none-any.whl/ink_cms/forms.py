from django import forms


class SharedInkForm(forms.ModelForm):
    def clean(self, *args, **kwargs):
        return super().clean(*args, **kwargs)


class ArticleForm(SharedInkForm):
    pass


class BlogEntryForm(SharedInkForm):
    pass


class PageForm(SharedInkForm):
    pass
