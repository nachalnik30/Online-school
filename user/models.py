from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property


class StudentAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='student_account',
                                blank=True,
                                null=True)

    def __str__(self):
        return "Student:{} {}".format(self.user.username, self.id)


class TeacherAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='teacher_account',
                                blank=True,
                                null=True)

    def __str__(self):
        return "Teacher: {} {}".format(self.user.username, self.id)


def user_directory_path(instance, filename):
    return 'user_{}/avatars/{}'.format(instance.id, filename)

class User(AbstractUser):
    STUDENT = 0
    TEACHER = 1
    account_type_choices = (
        (STUDENT, "Student"),
        (TEACHER, "Teacher")
    )

    REQUIRED_FIELDS = ["email", "account_type", "first_name", "last_name"]

    username = models.CharField(max_length=150, null=False, blank=False, unique=True)

    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    account_type = models.IntegerField(choices=account_type_choices, default=STUDENT)
    avatar_img = models.ImageField(upload_to=user_directory_path, default="media/blank_avatar.png")

    @cached_property
    def is_student(self):
        return self.account_type == 0

    @cached_property
    def is_teacher(self):
        return self.account_type == 1

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return "{}: {}".format(self.username, self.id)