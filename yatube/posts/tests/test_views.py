from django.test import Client, TestCase
from django.urls import reverse
from time import sleep

from ..models import Post, Group, User
from ..forms import PostForm


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petr')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        sleep(0.01)
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 2',
            group=cls.group_2
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self) -> None:
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        expected = list(Post.objects.select_related('group').all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_page_show_correct_context(self) -> None:
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})))
        expected = list(self.group.posts.all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_page_show_correct_context(self) -> None:
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:profile',
                    kwargs={'username': self.user})))
        expected = list(self.post.author.posts.all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_page_show_correct_context(self) -> None:
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author, self.post.author)
        self.assertEqual(response.context['post'].group, self.post.group)

    def test_post_create_page_show_correct_context(self) -> None:
        """Шаблон post_create сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_show_correct_context(self) -> None:
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_with_group(self):
        """Проверка: пост попадает в нужную группу."""
        self.assertEqual(self.post_2.group.title, 'Тестовая группа 2')
        self.assertEqual(self.post_2.text, 'Тестовый пост 2')

    def test_post_correct_appear(self):
        """Проверка: пост появляется на нужной странице."""
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        }
        for page in page_names:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.context['page_obj'][0], self.post_2)
