from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField("О себе", blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


class Category(models.Model):
    name = models.CharField("Название", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
    ]

    STATUS_CHOICES = [
        ("todo", "Нужно сделать"),
        ("in_progress", "В работе"),
        ("review", "Ревью"),
        ("blocked", "Ждёт связанные таски"),
        ("ready_test", "Готово к тестированию"),
        ("testing", "Тестирование"),
        ("tested", "Протестировано"),
        ("ready_deploy", "Готово к деплою"),
        ("done", "Выполнено"),
    ]

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(
        "Оценка времени (часы)", null=True, blank=True
    )
    priority = models.CharField(
        "Приоритет", max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="todo"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="tasks",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Исполнитель",
        related_name="tasks",
    )
    blocked_by = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="blocking",
        verbose_name="Блокируется задачами",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        return self.status == "done"
