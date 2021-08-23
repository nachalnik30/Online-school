from django.db import models
from user.models import TeacherAccount, StudentAccount

# Create your models here.


class Classroom(models.Model):
    teacher = models.ForeignKey(TeacherAccount,
                                on_delete=models.CASCADE,
                                related_name="classrooms")
    students = models.ManyToManyField(StudentAccount,
                                      related_name="classrooms")
    small_description = models.TextField(max_length=100, default="Без описания")
    name = models.TextField(max_length=50)


class Lesson(models.Model):
    classroom = models.ForeignKey(Classroom,
                                  on_delete=models.CASCADE,
                                  related_name="lessons")
    oral_part = models.TextField(max_length=5000)
    name = models.TextField(max_length=100)


class Task(models.Model):
    CHOICES_TYPE = 0
    INPUT_TYPE = 1
    CORRELATE_TYPE = 2

    task_type_choices = (
        (CHOICES_TYPE, "Choices"),
        (INPUT_TYPE, "Input"),
        (CORRELATE_TYPE, "Correlate")
    )

    lesson = models.ForeignKey(Lesson,
                               on_delete=models.CASCADE,
                               related_name="tasks")
    text = models.TextField(max_length=250)
    task_type = models.IntegerField(choices=task_type_choices, default=CHOICES_TYPE)


class Answer(models.Model):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name="answers",
                             null=False, blank=False)
    text = models.TextField(max_length=250, null=False, blank=False)
    is_correct = models.BooleanField(default=False)
