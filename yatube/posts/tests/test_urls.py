from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='100',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/<str:username>/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/100/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/<post_id>/edit/ доступна авторизованному
           пользователю."""
        response = self.authorized_client.get('/posts/100/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/<post_id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/posts/100/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/100/edit/'))

    def test_unexisting_page_url_exists_at_desired_location(self):
        """"Страница /unexisting_page/ ведёт к ошибке 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/100/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                responce = self.authorized_client.get(address)
                self.assertTemplateUsed(responce, template)
