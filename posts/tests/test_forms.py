import shutil
import tempfile

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files import File

from posts.models import User, Post, Group, Comment, Follow
from posts.forms import PostForm


class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.test_user = User.objects.create(
            username='testUserForm',
            email='testauthor@test.com',
            password='TestPassword')

        cls.author_follow = User.objects.create(
            username='Author_follow_test',
            email='testauthor@test.com',
            password='TestPassword')

        cls.group = Group.objects.create(
            title='Test Name',
            slug='testGroupForm',
            description='Test group for test_models'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст для формы',
            author=cls.test_user,
            group=cls.group
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.user = self.test_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Test: при отправке формы создаётся новая запись в базе данных"""

        post_count = Post.objects.count()
        form_data = {
            'text': 'Test form',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_text_labels(self):
        """Test: поля labels_list из form совпадает с ожиданием"""

        labels_list = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for value, expected in labels_list.items():
            with self.subTest(value=value):
                text_label = self.form.fields[value].label
                self.assertEqual(text_label, expected)

    def test_text_help_text(self):
        """Test: поля help_text из form совпадает с ожиданием"""

        text_help_text = self.form.fields['text'].help_text
        self.assertEqual(text_help_text, 'Введите текст')

    def test_post_change(self):
        """Test:при редактировании поста через форму
        на странице /<username>/<post_id>/edit/ изменяется соответствующая
        запись в базе данных"""

        save_old_text = self.post.text
        form = {'text': f': edit done!',
                'group': self.post.group.id
                }
        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}), data=form, follow=True)
        self.post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('post',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}))
        self.assertNotEqual(self.post.text, save_old_text)

    def test_upload_not_img_file(self):
        """Test: проверка защиты от загрузки «неправильных» файлов"""

        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.name = 'test.txt'

        obj_count = Post.objects.count()
        form = {'text': f': edit done!',
                'group': self.post.group.id,
                'image': File(tmp_file)
                }
        response = self.authorized_client.post(reverse('new_post'),
                                               data=form, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), obj_count)

        tmp_file.close()

    def test_comment(self):
        """Только авторизированный пользователь может комментировать посты"""

        form = {'text': 'test comment form',
                'button': True}

        # Авторизированный пользователь
        comment_count = Comment.objects.count()
        self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}),
            data=form, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

        # Неавторизированный пользователь
        comment_count = Comment.objects.count()
        self.guest_client.post(
            reverse('add_comment',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}),
            data=form, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_follow(self):
        """Test: Авторизованный пользователь может подписываться на других
        пользователей"""

        # Подписка
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.author_follow}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        """Test: Авторизованный пользователь может удалять из подписок
        других пользователей"""

        # Подписываем test_user на автора
        Follow.objects.create(
            user=self.test_user,
            author=self.author_follow
        )

        # Отписка
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.author_follow}))
        self.assertNotEqual(Follow.objects.count(), follow_count)
