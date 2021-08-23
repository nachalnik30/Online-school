from user import tasks
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response


from classroom.models import Classroom, Lesson
from classroom.serializers import CheckLessonResultsSerializer, ClassroomCreateListSerializer, LessonAddSerializer, ClassroomRetrieveUpdateDestorySerializer, LessonDetailSerializer


class ClassroomCreateListApiView(generics.ListCreateAPIView):
    serializer_class = ClassroomCreateListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            queryset = Classroom.objects.filter(teacher__id=user.teacher_account.id)
        else:
            queryset = Classroom.objects.filter(students__id=user.student_account.id)

        return queryset


class ClassroomAddLesson(generics.CreateAPIView):
    serializer_class = LessonAddSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        uri = self.request.build_absolute_uri()
        classroom_id = uri.split("/")[-3]
        context.update({'classroom_id': classroom_id})
        return context


class ClassroomRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassroomRetrieveUpdateDestorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            queryset = Classroom.objects.filter(teacher__id=user.teacher_account.id)
        else:
            queryset = Classroom.objects.filter(students__id=user.student_account.id)

        return queryset


class LessonRetrieveUpdateDestroyApiView(generics.RetrieveDestroyAPIView):
    serializer_class = LessonDetailSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Lesson.objects.all()

        return queryset


class CheckLessonResultsView(generics.GenericAPIView):

    def post(self, request, pk):

        tasks_serializer = CheckLessonResultsSerializer(data=request.data, context={"lesson_id": pk})
        if tasks_serializer.is_valid():
            print(tasks_serializer.data)
        else:
            return Response(tasks_serializer.errors)

        return Response("success", 200)