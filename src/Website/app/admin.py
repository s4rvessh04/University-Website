from django.contrib import admin
from .models import Semester, Student, Teacher, Subject, Academic, Branch, InternshipApplicant, ApiUser


admin.site.register(Semester)
admin.site.register(Branch)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Academic)
admin.site.register(InternshipApplicant)
admin.site.register(ApiUser)
