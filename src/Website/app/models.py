from django.db import models
from django.contrib.auth.models import User


class Branch(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class Semester(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=False, blank=True)

    def __str__(self):
        return str(self.name)


class Subject(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    marks = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Academic(models.Model):
    teacher = models.ForeignKey(Teacher, null=True, on_delete=models.SET_NULL)
    student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
    semester = models.ForeignKey(
        Semester, null=True, on_delete=models.SET_NULL)
    marks = models.FloatField(null=True)

    def __str__(self):
        return str(self.student.name)


class InternshipApplicant(models.Model):
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    qualificationAndqueries = models.TextField()

    def __str__(self):
        return str(self.email)


class ApiUser(models.Model):
    email = models.EmailField(max_length=200)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.email)
