from django import forms
from django.utils.translation import gettext_lazy as _

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": _("Текст"),
            "group": _("Группа"),
        }
        help_texts = {
            "text": _("Введите текст")
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
