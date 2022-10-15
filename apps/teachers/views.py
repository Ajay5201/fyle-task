from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from apps.teachers.models import Teacher
from apps.students.models import Assignment, Student
from .serializers import TeacherAssignmentSerializer


class AssignmentsView(generics.ListCreateAPIView):
    serializer_class = TeacherAssignmentSerializer

    def get(self, request, *args, **kwargs):
        assignments = Assignment.objects.filter(teacher__user=request.user)

        return Response(
            data=self.serializer_class(assignments, many=True).data,
            status=status.HTTP_200_OK
        )


    def patch(self, request, *args, **kwargs):
        try:
            assignment = Assignment.objects.get(pk=request.data['id'], teacher__user=request.user)
        except Assignment.DoesNotExist:
            if 'student' in request.data and request.data['student']:
                data={'non_field_errors': ['Teacher cannot change the student who submitted the assignment']}
            if 'grade' in request.data and request.data['grade']:
                data={'non_field_errors': ['Teacher cannot grade for other teacher''s assignment']}
            return Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST
                )
        request.data['state'] = assignment.state

        serializer = self.serializer_class(assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
