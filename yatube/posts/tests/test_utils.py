from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petr')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for num_of_post in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {num_of_post}',
                id=num_of_post,
                group=cls.group
            )
        cls.list_of_reverses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user})
        ]

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверка вывода 10 статей на первой странице."""
        for reversing in self.list_of_reverses:
            response = self.guest_client.get(reversing)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        """Проверка вывода 3 статей на второй странице."""
        for reversing in self.list_of_reverses:
            response = self.guest_client.get(reversing + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)