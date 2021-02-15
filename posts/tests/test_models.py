from django.test import TestCase

from datetime import datetime as dt

from posts.models import Post, Group, User


class PostGroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create(
            username='test-user',
            email='testauthor@test.com',
            password='TestPassword')

        cls.group = Group.objects.create(
            title='Test name',
            slug='test-group',
            description='Test group test_models'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=dt.now(),
            author=cls.author,
            group=cls.group
        )

    def test_post_verbose_name(self):
        """Test: поля verbose_name из post совпадает с ожиданием"""

        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """Test: поля help_text из post совпадает с ожиданием"""

        post = self.post
        field_help_text = {
            'text': 'Напишите здесь что-нибудь',
            'pub_date': 'Дата указывается автоматически',
            'author': 'Это поле заполняется автоматически',
            'group': 'Необязательное поле'
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_object_name_is_title_fild(self):
        """Test: правильно ли отображается значение поля __str__ для post"""

        post = self.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_post_object_name_len(self):
        """Test: правильно ли отображается значение поля __str__ для post
        (первые пятнадцать символов поста)"""

        post = self.post
        expected_object_name = post.text[:15]
        self.assertLessEqual(len(expected_object_name), 15)

    def test_group_verbose_name(self):
        """Test: поля verbose_name из group совпадает с ожиданием"""

        group = self.group
        field_verboses = {
            'title': 'Группа',
            'slug': 'Слаг',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        """Test: поля help_text из group совпадает с ожиданием"""

        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': (
                    'Укажите адрес для страницы задачи. Используйте только ' +
                    'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Описагие группы'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_group_object_name_is_title_fild(self):
        """Test: правильно ли отображается значение поля __str__ для group"""

        group = self.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
