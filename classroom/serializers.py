import copy

from rest_framework import serializers

from classroom.models import Classroom, Lesson, Task, Answer
from user.serializers import TeacherSerializer, StudentSerializer, TeacherDetailSerializer, StudentDetailSerializer
from user.models import StudentAccount, TeacherAccount


class ClassroomCreateListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classroom
        fields = ['name']

    def create(self, validated_data):

        if self.context['request'].user.is_teacher:
            validated_data['teacher'] = self.context['request'].user.teacher_account
            return super().create(validated_data)
        else:
            raise serializers.ValidationError({"detail": "Класс может быть создан только учителем."})


class ClassroomRetrieveUpdateDestorySerializer(serializers.ModelSerializer):
    students = StudentDetailSerializer(many=True, read_only=True)
    teacher = TeacherDetailSerializer(read_only=True)
    lessons = serializers.PrimaryKeyRelatedField(many=True, queryset=Lesson.objects.all())

    class Meta:
        model = Classroom
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct',]

        extra_kwargs = {
            "is_correct": {
                "write_only": True
            }
        }


class TaskSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Task
        fields = ['id', 'text', "task_type", "answers"]

        extra_kwargs = {
            "task_type": {
                "required": True
            }
        }


class LessonAddSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ['id', 'oral_part', 'name', 'tasks', 'classroom']

        extra_kwargs = {
            "classroom": {
                "read_only": "True"
            }
        }

    def create(self, validated_data):
        classroom_id = self.context['classroom_id']
        classroom = Classroom.objects.get(id=classroom_id)
        lesson = Lesson.objects.create(classroom=classroom, name=validated_data['name'], oral_part=validated_data['oral_part'])

        for task in validated_data['tasks']:
            task_instance = Task.objects.create(text=task['text'], lesson=lesson, task_type=task['task_type'])
            answers = []
            for answer in task['answers']:
                answers.append(Answer.objects.create(text=answer['text'], is_correct=answer['is_correct'], task=task_instance))
            task_instance.save()

        lesson.save()

        return lesson

    def validate(self, validated_data):
        classroom_id = self.context.get("classroom_id")
        if not Classroom.objects.filter(id=classroom_id).exists():
            raise serializers.ValidationError({"detail": "Не найден класс с таким ID."}, 400)

        return validated_data


class LessonDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ['id', 'oral_part', 'name', 'tasks', 'classroom']

        extra_kwargs = {
            "classroom": {
                "read_only": "True"
            },
        }


class CheckLessonTasksSerializer(serializers.Serializer):
    error_messages_ = {
        "task_wrong_id": "Не найдено задания с таким ID в переданном уроке.",
        "answer_wrong_id": "Не найден ответ с таким ID в переданном задании."
    }

    task_id = serializers.IntegerField(required=True)
    answers_id = serializers.ListField(child=serializers.IntegerField())
    is_correct = serializers.BooleanField(required=False)

    def validate(self, data):
        task_id = data['task_id']
        answers_id = data['answers_id']
        lesson_id = self.context['lesson_id']

        task = Task.objects.filter(id=task_id, lesson_id=lesson_id)
        if task.exists():
            for answer_id in answers_id:
                answer = Answer.objects.filter(task_id=task_id, id=answer_id)
                if not answer.exists():
                    raise serializers.ValidationError({"answer_id": self.error_messages_['answer_wrong_id']})
        else:
            raise serializers.ValidationError({"task_id": self.error_messages_['task_wrong_id']})
        return data


class CheckLessonResultsSerializer(serializers.Serializer):
    tasks = CheckLessonTasksSerializer(many=True)

    def validate(self, data):

        for task in data['tasks']:
            answers_id = task['answers_id']
            answers = Answer.objects.filter(id__in=answers_id).values('is_correct')
            answers_full = [answer['is_correct'] for answer in answers]

            task['is_correct'] = True if all(answers_full) else False

        return data
