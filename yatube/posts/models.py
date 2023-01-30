from django.db import models
from django.contrib.auth import get_user_model
from yatube.settings import LEN_POST


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Адрес')
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title

    class Meta():
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    def __str__(self) -> str:
        return self.text[:LEN_POST]

    class Meta():
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'
