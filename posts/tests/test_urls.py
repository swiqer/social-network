from django.test import TestCase, Client, modify_settings
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.urls import reverse

from posts.models import Post, Group, User


@modify_settings(
        MIDDLEWARE={
            'append': 'django.contrib.flatpages.middleware'
                      '.FlatpageFallbackMiddleware'}
    )
class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site1 = Site(pk=1, domain='example.com', name='example.com')
        cls.site1.save()
        cls.about_author = FlatPage.objects.create(
            url='/about_author/', title='Об авторе', content='Мой GitHub'
        )
        cls.about_spec = FlatPage.objects.create(
            url='/about_spec/', title='Технологии',
            content='Python, Django'
        )
        cls.about_author.sites.add(cls.site1)
        cls.about_spec.sites.add(cls.site1)

        cls.test_user = User.objects.create(
            username='testUser',
            email='testauthor@test.com',
            password='TestPassword')

        cls.not_author = User.objects.create(
            username='not_the_author',
            email='testauthor@test.com',
            password='TestPassword')

        cls.group = Group.objects.create(
            title='Test Name',
            slug='testGroup',
            description='Test group for test_models'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.get(username='testUser'),
            group=Group.objects.get(slug='testGroup')
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = self.test_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user2 = self.not_author
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user2)

    def test_urls_client(self):
        """Тест: доступность страниц по URL"""

        urls_list = {
            reverse('index'): 200,
            reverse('group', kwargs={'slug': self.group.slug}): 200,
            reverse('group', kwargs={'slug': 'test'}): 404,
            reverse('profile',
                    kwargs={'username': self.test_user.username}): 200,
            reverse('post',
                    kwargs={'username': self.test_user.username,
                            'post_id': self.post.pk}): 200
        }
        for value, expected in urls_list.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(response.status_code, expected), value

    def test_url_new_redirect_anonymous_on_login(self):
        """Test: доступность страниц в соответствии с правами пользователея:
        guest_client"""

        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response,
                             reverse('login')+'?next='+reverse('new_post'))

    def test_url_new_authorized_client(self):
        """Test: доступность страниц в соответствии с правами пользователея:
        authorized_client"""

        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """Тест: какой шаблон будет вызван при обращении
        к соответствуюему URL"""

        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': self.group.slug}),
            'posts/new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url(self):
        """Test: доступность страницы редактирования поста
        /<username>/<post_id>/edit/ для
        - анонимного пользователя;
        - авторизованного пользователя — автора поста;
        - авторизованного пользователя — не автора поста."""

        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}))
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.post.author.username,
                                         'post_id': self.post.pk}))

        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}))
        self.assertEqual(response.status_code, 200)

        response = self.authorized_client_not_author.get(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}))
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.post.author.username,
                                         'post_id': self.post.pk}))

    def test_flatpages(self):
        """Test: доступность страниц flatpages по URL"""

        flatpages_urls = {
            reverse('about-author'): 200,
            reverse('about-spec'): 200
        }
        for url, status_code in flatpages_urls.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)
