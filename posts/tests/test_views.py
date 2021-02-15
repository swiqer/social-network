import shutil
import tempfile
import os

from PIL import Image

from django.test import Client, TestCase, modify_settings
from django.urls import reverse
from django import forms
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.conf import settings
from django.core.files import File

from posts.models import Group, Post, User, Follow


@modify_settings(
    MIDDLEWARE={
        'append': 'django.contrib.flatpages.middleware'
                  '.FlatpageFallbackMiddleware'}
)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.site1 = Site(pk=1, domain='example.com', name='example.com')
        cls.site1.save()
        cls.about_author = FlatPage.objects.create(
            url='/about_author/', title='Об авторе', content='Мой '
        )
        cls.about_spec = FlatPage.objects.create(
            url='/about_spec/', title='Технологии',
            content='Python, Django'
        )
        cls.about_author.sites.add(cls.site1)
        cls.about_spec.sites.add(cls.site1)

        cls.view_user = User.objects.create(
            username='view-user',
            first_name='Дядя',
            last_name='Ваня',
            email='testauthor@test.com',
            password='TestPassword')

        cls.group = Group.objects.create(
            title='View name',
            slug='test-view',
            description='Test '
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.view_user,
            group=cls.group
        )

        cls.user1 = User.objects.create(
            username='User1',
            email='testauthor@test.com',
            password='TestPassword')

        cls.user2 = User.objects.create(
            username='User2',
            email='testauthor@test.com',
            password='TestPassword')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.user = self.view_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user_1 = self.user1
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        self.user_2 = self.user2
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_pages_uses_correct_template(self):
        """Тест: какой шаблон будет вызван при обращении к view-классам
        через соответствующий name"""

        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': self.group.slug}),
            'posts/new_post.html': reverse('new_post'),
            'posts/new_post.html':
                reverse('post_edit',
                        kwargs={'username': self.post.author.username,
                                'post_id': self.post.pk})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_list_page_show_correct_context(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове index"""

        response = self.guest_client.get(reverse('index'))

        task_text = response.context.get('page')[0].text
        self.assertEqual(task_text, self.post.text)

        task_author = response.context.get('page')[0].author
        self.assertEqual(task_author, self.post.author)

        task_pub_date = response.context.get('page')[0].pub_date
        self.assertEqual(task_pub_date, self.post.pub_date)

    def test_group_list_page_show_correct_context(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове group/slug"""

        response = self.guest_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))

        task_group = response.context.get('group').title
        self.assertEqual(task_group, self.group.title)

    def test_new_and_edit_page_show_correct_context(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове new_post и post_edit"""

        response = self.authorized_client.get(reverse('new_post'))
        response2 = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

                form_field2 = response2.context.get('form').fields.get(value)
                self.assertIsInstance(form_field2, expected)

    def test_correct_posting(self):
        """Тест: если при создании поста указать группу, то этот пост
        появляется на главной странице сайта, на странице выбранной группы."""

        post = Post.objects.create(
            text='Test correct posting',
            author=self.view_user,
            group=self.group
        )
        response = self.guest_client.get(reverse('index'))
        find_post_on_index_page = response.context.get('page')[0].pk
        self.assertEqual(find_post_on_index_page, post.pk)

        response = self.guest_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))
        find_post_on_group_page = response.context.get('page')[0].pk
        self.assertEqual(find_post_on_group_page, post.pk)

    def test_user_page_show_correct_context(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове profile/username"""

        response = self.guest_client.get(
            reverse('profile', kwargs={'username': self.post.author.username})
        )
        text = response.context.get('page')[0].text
        self.assertEqual(text, self.post.text)

        author = response.context.get('page')[0].author
        self.assertEqual(author, self.post.author)

        pub_date = response.context.get('page')[0].pub_date
        self.assertEqual(pub_date, self.post.pub_date)

        posts_count = response.context.get('posts_count')
        self.assertEqual(posts_count,
                         Post.objects.filter(author=self.view_user).count())

        user_title = response.context.get('user_title')
        self.assertEqual(user_title, self.view_user.get_full_name())

        username = response.context.get('username')
        self.assertEqual(username.username, self.post.author.username)

    def test_user_post_page_correct_context(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове post/username/post_id"""

        response = self.guest_client.get(
            reverse('post',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}
                    )
        )
        text = response.context.get('post').text
        self.assertEqual(text, self.post.text)

        author = response.context.get('post').author
        self.assertEqual(author, self.post.author)

        pub_date = response.context.get('post').pub_date
        self.assertEqual(pub_date, self.post.pub_date)

        posts_count = response.context.get('posts_count')
        self.assertEqual(posts_count,
                         Post.objects.filter(author=self.view_user).count())

        user_title = response.context.get('user_title')
        self.assertEqual(user_title, self.view_user.get_full_name())

        username = response.context.get('username')
        self.assertEqual(username.username, self.post.author.username)

    def test_index_page_paginator(self):
        """Test: в словарь context главной страницы передаётся не более
        установленного количества постов"""

        Post.objects.create(
            text='Test correct paginator',
            author=self.view_user,
            group=self.group
        )
        response = self.guest_client.get(reverse('index'))
        count_posts = len(response.context.get('page'))
        self.assertLessEqual(count_posts, 10)

    def test_flatpage_about_author(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове flatpage /about_author/"""

        response = self.guest_client.get(reverse('about-author'))
        context = response.context.get('flatpage')
        self.assertEqual(context.title, self.about_author.title)
        self.assertEqual(context.content, self.about_author.content)

    def test_flatpage_about_spec(self):
        """Тест: соответствует ли ожиданиям словарь context,
        передаваемый в шаблон при вызове flatpage /about_spec/"""

        response = self.guest_client.get(reverse('about-spec'))
        context = response.context.get('flatpage')
        self.assertEqual(context.title, self.about_spec.title)
        self.assertEqual(context.content, self.about_spec.content)

    def test_img_tag(self):
        """Test: на странице есть тег <img>"""

        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.name = 'test.png'
        img = Image.new('RGB', (60, 30), color='red')
        img.save(tmp_file)

        img_post = Post.objects.create(
            text='Test correct img tag',
            author=self.view_user,
            group=self.group,
            image=File(tmp_file)
        )
        response = self.guest_client.get(
            reverse('post', kwargs={'username': img_post.author.username,
                                    'post_id': img_post.pk}))
        self.assertContains(response, '<img class="card-img"',
                            status_code=200)

        response = self.guest_client.get(reverse('index'))
        self.assertContains(response, '<img class="card-img"',
                            status_code=200)

        response = self.guest_client.get(
            reverse('profile', kwargs={'username': img_post.author.username}))
        self.assertContains(response, '<img class="card-img"',
                            status_code=200)

        response = self.guest_client.get(
            reverse('group', kwargs={'slug': img_post.group.slug}))
        self.assertContains(response, '<img class="card-img"',
                            status_code=200)

        tmp_file.close()

    def test_follow_page(self):
        """Test: Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него."""

        # Автор постов
        author = User.objects.create(
            username='Author',
            email='testauthor@test.com',
            password='TestPassword')

        # Подписываем user1 на автора, user2 не подписываем
        Follow.objects.create(
            user=self.user1,
            author=author
        )

        # Пост автора
        test_post = Post.objects.create(
            text='Test follow page',
            author=author,
            group=self.group
        )

        # Проверка поста на странице /follow у user1
        response = self.authorized_client_1.get(reverse('follow_index'))
        text = response.context.get('page')[0].text
        self.assertEqual(text, test_post.text)

        # Проверка поста на странице /follow у user2
        text = None
        response = self.authorized_client_2.get(reverse('follow_index'))
        try:
            text = response.context.get('page')[0].text
        except Exception:
            pass
        self.assertNotEqual(text, test_post.text)
