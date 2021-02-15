from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста",
                            help_text="Напишите здесь что-нибудь")
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                    verbose_name="Дата публикации",
                                    help_text="Дата указывается автоматически")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор поста",
                               help_text="Это поле заполняется автоматически")
    group = models.ForeignKey("Group", on_delete=models.SET_NULL, blank=True,
                              null=True, related_name="posts",
                              verbose_name="Группа",
                              help_text="Необязательное поле")
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name="Изображение",
                              help_text="Необязательное поле"
                              )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Группа",
                             help_text="Название группы")
    slug = models.SlugField(
        unique=True, null=True, verbose_name="Слаг",
        help_text=((
                "Укажите адрес для страницы задачи. Используйте только " +
                "латиницу, цифры, дефисы и знаки подчёркивания")))
    description = models.TextField(verbose_name="Описание",
                                   help_text="Описагие группы")

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE,
                             related_name="comments",
                             verbose_name="Пост",
                             help_text="Это поле заполняется автоматически")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор поста",
                               help_text="Это поле заполняется автоматически")
    text = models.TextField(verbose_name="Комментарий",
                            help_text="Ваш коментарий")
    created = models.DateTimeField(auto_now_add=True, db_index=True,
                                   verbose_name="Дата публикации",
                                   help_text="Дата указывается автоматически")

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Пользователь",
                             help_text="Это поле заполняется автоматически")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name="Подписка на автора",
                               help_text="Это поле заполняется автоматически")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_object"),
        ]
