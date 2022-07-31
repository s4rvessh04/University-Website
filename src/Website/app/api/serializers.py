from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from app.models import *


class UsersSerializer(serializers.HyperlinkedModelSerializer):
    api_token = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='api:token')

    class Meta:
        model = User
        fields = ['username', 'email', 'api_token', 'date_joined']


class AcademicSerializer(serializers.ModelSerializer):
    student = serializers.CharField(read_only=True, source='student.name')
    subject = serializers.CharField(read_only=True, source='subject.name')
    semester = serializers.CharField(read_only=True, source='semester.name')

    class Meta:
        model = Academic
        fields = ['student', 'semester', 'subject', 'marks']


class StudentSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True, source='branch.name')

    class Meta:
        model = Student
        fields = ['name', 'branch', 'phone']


class AllAcademicSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(read_only=True, source="subject.name")
    semester = serializers.CharField(read_only=True, source="semester.name")
    student = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api:student-details')
    student_name = serializers.CharField(read_only=True, source="student.name")

    class Meta:
        model = Academic
        fields = ['student_name', 'student',
                  'subject', 'marks', 'semester']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        exclude = ['user']


class InternshipApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplicant
        exclude = ['id']
        fields = '__all__'
