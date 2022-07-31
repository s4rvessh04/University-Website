from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse

from app.models import Academic, Student, Teacher, InternshipApplicant, ApiUser
from app.forms import CareersInternshipform, ApiUserRegistrationForm, UpdateUserDetails

from rest_framework.authtoken.models import Token


def home_view(request, *args, **kwargs):
    return render(request, 'index.html', {})


def error404_view(request, *args, **kwargs):
    return render(request, '404.html', {})


def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def campus_view(request, *args, **kwargs):
    return render(request, 'campus.html', {})


def placements_view(request, *args, **kwargs):
    return render(request, 'placements.html', {})


def admissions_view(request, *args, **kwargs):
    return render(request, 'admissions.html', {})


def developers_view(request, *args, **kwargs):
    return render(request, 'developers.html', {})


def api_docs_view(request, *args, **kwargs):
    context = {
        'link_link': request.build_absolute_uri(reverse('api:links')),
    }

    return render(request, 'api_documentation.html', context)


def profile_view(request, *args, **kwargs):
    user = request.user
    email = user.email
    name = None
    branch = None
    token = None
    account_type = user.groups.all()[0].name

    if account_type == 'student':
        student = Student.objects.get(user=user)
        name = student.name
        branch = student.branch.name
        try:
            token = Token.objects.get(user=user).key
        except Token.DoesNotExist:
            pass
    elif account_type == 'teacher':
        teacher = Teacher.objects.get(user=user)
        name = teacher.name
    else:
        print('Check for error here!')

    context = {
        'name': name,
        'user': user,
        'email': email,
        'account_type': account_type,
        'branch': branch,
        'token': token,
    }

    return render(request, 'users/profile.html', context)


def change_account_settings(request, *args, **kwargs):
    """
    User update form

    Fields:
    - Username
    - Password
    """
    form = UpdateUserDetails()
    if request.method == "POST":
        form = UpdateUserDetails(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = User.objects.get(username=request.user)
            if username and password:
                user.set_password(password)
                user.save()
                User.objects.filter(username=user).update(username=username)
                messages.success(
                    request, "Updated Successfully. Log In to continue.")
                return redirect('login_view')
            elif password:
                user.set_password(password)
                user.save()
                messages.success(
                    request, "Password updated Successfully.Log In with new password.")
                return redirect('login_view')
            elif username:
                User.objects.filter(username=user).update(username=username)
                messages.success(request, "Username Updated Successfully.")
            else:
                messages.error(
                    request, "Username or password cannot be empty!")
                return redirect('account_settings')
        else:
            messages.error(request, 'Username is used!')

    context = {
        'form': form,
    }

    return render(request, 'users/account_settings.html', context)


def developers_register_view(request, *args, **kwargs):
    """
    API registration form.

    Fields:
    - email
    """
    form = ApiUserRegistrationForm()
    if request.method == 'POST':
        form = ApiUserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                if ApiUser.objects.filter(email=email).exists():
                    messages.warning(
                        request, 'You have already registerd for developers program!')
                    url = reverse('developers_register_view')
                    return HttpResponseRedirect(url)
                token = Token.objects.create(user=user)
                form.save()
                ApiUser.objects.filter(email=email).update(user=user)
                messages.info(request, 'Your Token: ' + token.key)
            except User.DoesNotExist:
                messages.error(
                    request, 'The email entered is not associated with college!')
                return HttpResponseRedirect(reverse('developers_register_view'))

    return render(request, 'developers_register.html', {'form': form})


def careers_view(request, *args, **kwargs):
    """
    Form for internship applicants in career url.

    Fields:
    - email
    - phone
    - location
    - qualification and queries
    """
    form = CareersInternshipform()
    if request.method == 'POST':
        form = CareersInternshipform(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            location = form.cleaned_data.get('location')
            qualificationAndqueries = form.cleaned_data.get(
                'qualificationAndqueries')
            try:
                InternshipApplicant.objects.get(email=email)
                messages.error(
                    request, 'You have successfully sent you request already.')
            except InternshipApplicant.DoesNotExist:
                form.save()
                messages.success(request, 'Sent Successfully')

            form = CareersInternshipform()
            return HttpResponseRedirect('#internships')

    context = {
        "form": form,
    }

    return render(request, 'careers.html', context)


def student_details_chart(request, user):
    """
    Return lables and data for student page.
    (All semester wise)
    """
    academic_list = Academic.objects.all()
    user = User.objects.get(username=user)
    student_academic_list = Academic.objects.filter(student__user=user)
    sem_dict = {}

    for sem in student_academic_list:
        sem_dict[sem.semester.name] = 0
        for obj in Academic.objects.filter(student__user=user, semester__name=sem.semester.name):
            sem_dict[obj.semester.name] += obj.marks

    return JsonResponse(data={
        'labels': list(sem_dict.keys()),
        'defaultData': list(sem_dict.values()),
    })


def student_current_sem_chart(request, user):
    """
    Return lables and data for the student page.
    (Current semester subject wise)
    """
    academic_list = Academic.objects.all()
    user = User.objects.get(username=user)
    student_academic_list = Academic.objects.filter(student__user=user)
    sem_dict = {}
    sems = [academic.semester.name for academic in student_academic_list]
    if sems:
        student_academic_list = Academic.objects.filter(
            student__user=user, semester__name=sems[-1])

    for item in student_academic_list:
        sem_dict[item.subject.name] = item.marks

    return JsonResponse(data={
        'labels': list(sem_dict.keys()),
        'defaultData': list(sem_dict.values()),
    })
