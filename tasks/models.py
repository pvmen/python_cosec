from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    STATUS_CHOICES = [
        ('todo', 'Нужно сделать'),
        ('in_progress', 'В работе'),
        ('review', 'Ревью'),
        ('blocked', 'Ждёт связанные таски'),
        ('ready_test', 'Готово к тестированию'),
        ('testing', 'Тестирование'),
        ('tested', 'Протестировано'),
        ('ready_deploy', 'Готово к деплою'),
        ('done', 'Выполнено'),
    ]

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    deadline = models.DateTimeField('Дедлайн', null=True, blank=True)
    priority = models.CharField(
        'Приоритет',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Исполнитель',
        related_name='tasks'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        return self.status == 'done'
