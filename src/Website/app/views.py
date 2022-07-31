from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.db.models import Q

from .models import Student, Teacher, Academic, Semester, Branch, ApiUser
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users
from .filters import AcademicFilter, StudentFilter


@login_required(login_url='login_view')
@allowed_users(['admin'])
def register_view(request):
    """
    Creates User, based on the group selected.
    If group is student then branch is to be selected, if not will throw an error.
    If group is teacher then no need for the branch to be selected.
    """
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already Exists')
            else:
                username = form.cleaned_data.get('username')

                if form.cleaned_data.get('is_teacher') == True:
                    user = form.save()
                    group = Group.objects.get(name='teacher')
                    user.groups.add(group)
                    Teacher.objects.create(user=user)
                    obj = Teacher.objects.filter(user=user).update(
                        name=form.cleaned_data.get('name'),
                        phone=form.cleaned_data.get('phone'))
                    messages.success(request, 'Created Teacher ' + username)
                else:
                    group = Group.objects.get(name='student')
                    dropdown_branch = form.cleaned_data.get('branch')

                    if dropdown_branch == 'None':
                        messages.error(request, 'Select Branch')
                    else:
                        user = form.save()
                        s = Student.objects.create(user=user)
                        branch = Branch.objects.get(name=dropdown_branch)
                        s.branch = branch
                        user.groups.add(group)
                        s.save()
                        Student.objects.filter(user=user).update(
                            name=form.cleaned_data.get('name'),
                            phone=form.cleaned_data.get('phone')
                        )
                        messages.success(
                            request, 'Created Student ' + username)
    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)


@login_required(login_url='login_view')
def user_view(request):
    """
    Returns users to respective group related pages.
    """
    obj = User.objects.get(username=request.user)
    group = obj.groups.all()[0].name
    student_list = Student.objects.all()
    query = request.GET.get('q')

    if query:
        student_list = Student.objects.filter(Q(user__username__icontains=query) |
                                              Q(name__icontains=query))
    details = {
        'obj': obj,
        'group': group,
        'student_list': student_list,
    }

    if group == 'student':
        return render(request, 'users/studentpage.html', details)
    elif group == 'teacher':
        return render(request, 'users/teacherpage.html', details)
    elif group == 'admin':
        return redirect('dashboard_view')
    else:
        return redirect('error404')


@unauthenticated_user
def login_view(request):
    """
    Verifies and logs users in.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Enter a valid email address')
            return render(request, 'users/login.html', {})

        try:
            username = User.objects.get(email=email)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('user_view')
            else:
                messages.error(request, 'Email or Passsword is incorrect')

        except ObjectDoesNotExist:
            messages.error(request, 'Email or Passsword is incorrect')

    return render(request, 'users/login.html', {})


@login_required(login_url='login_view')
def logout_view(request):
    """
    Logs users out of their sessions.
    """
    logout(request)
    return redirect('home')


@login_required(login_url='login_view')
@allowed_users(['teacher'])
def create_academic_record(request):
    """
    Creates an academic record one at a time.
    The no of inline forms can be changed with 'extra' kwarg.
    (Default is 5 as per each sem subject)
    """
    user = request.user
    student_list = Student.objects.all()
    semester_list = Semester.objects.all()
    branch_list = Branch.objects.all()
    Academic_formset = inlineformset_factory(Teacher, Academic, fields=(
        'teacher', 'subject', 'marks',), extra=4, can_delete=False)

    try:
        teacher = Teacher.objects.get(user=user)
        formset = Academic_formset(
            queryset=Academic.objects.none(), instance=teacher)
    except teacher.DoesNotExist:
        return HttpResponse('<h1>Check Login credential again</h1>')

    if request.method == 'POST':
        formset = Academic_formset(request.POST, instance=teacher)

        if formset.is_valid():
            dropdown_semester = request.POST.get('dropdown_semester', False)
            dropdown_student = request.POST.get('dropdown_student', False)
            if dropdown_semester and dropdown_student:
                semester = Semester.objects.get(name=dropdown_semester)
                student = Student.objects.get(name=dropdown_student)
                instances = formset.save()

                for instance in instances:
                    instance.student = student
                    instance.semester = semester
                    instance.save()
            else:
                return HttpResponse("<p>Form can't be empty! </p>")

    myfilter = StudentFilter(request.GET, queryset=student_list)
    student_list = myfilter.qs

    context = {
        'formset': formset,
        'myfilter': myfilter,
        'branch_list': branch_list,
        'student_list': student_list,
        'semester_list': semester_list,
    }

    return render(request, 'acedemic-form.html', context)


def academic_filter(request):
    """
    Filters student academic records as per their requirement.

    Filter Fields to filter:
    - semester
    - subject
    """
    academics = Academic.objects.all()
    user = User.objects.get(username=request.user)
    student = Student.objects.get(user=user)

    myfilter = AcademicFilter(request.GET, queryset=academics)
    academics = myfilter.qs

    context = {
        'myfilter': myfilter,
        'academics': academics,
        'student': student,
    }

    return render(request, 'filter_test.html', context)


@login_required(login_url='login_view')
@allowed_users(['admin'])
def dashboard_view(request):
    """
    Admin exclusive view, where all the users related data can be viewed.
    And contains filter for quicky finding the required user.

    Filter Fields include:
    - username
    - studentname
    - teachername
    """
    user_list = User.objects.all()
    student_list = Student.objects.all()
    teacher_list = Teacher.objects.all()

    user_count = user_list.count()
    student_count = student_list.count()
    teacher_count = teacher_list.count()
    apiuser_count = ApiUser.objects.count()

    query = request.GET.get('q')

    if query:
        user_list = User.objects.filter(Q(username__icontains=query)
                                        | Q(student__name__icontains=query)
                                        | Q(teacher__name__icontains=query))
        student_list = Student.objects.filter(Q(name__icontains=query))
        teacher_list = Teacher.objects.filter(Q(name__icontains=query))

    context = {
        'user_list': user_list,
        'student_list': student_list,
        'teacher_list': teacher_list,
        'user_count': user_count,
        'student_count': student_count,
        'teacher_count': teacher_count,
        'apiuser_count': apiuser_count,
    }
    return render(request, 'users/admin_dashboard.html', context)


def marks_and_percentage(user):
    """
    Returns the calculated semester marks and percentages.
    """
    all_sem_list = Academic.objects.filter(student__user=user)
    all_sems = {}
    count_sems = 0

    for sem in all_sem_list:
        if sem == None:
            break
        if sem.semester.name in all_sems:
            all_sems[sem.semester.name] += sem.marks
        else:
            all_sems[sem.semester.name] = sem.marks
            count_sems += 1

    all_sems_GRAND_TOTAL = float(sum(all_sems.values()))

    if count_sems != 0 and all_sems_GRAND_TOTAL != 0:
        all_sems_PERCENTAGE = float(
            (all_sems_GRAND_TOTAL / (count_sems*500))*100)
    else:
        all_sems_PERCENTAGE = None

    current_sem_TOTAL = 0
    current_sem_GRAND_TOTAL = float(0)

    if all_sems:
        current_sem_list = Academic.objects.filter(student__name=user.student.name, semester__name=list(
            all_sems.keys())[-1]) if user.groups.all()[0].name == 'student' else None
        for item in current_sem_list:
            current_sem_TOTAL += item.marks
            current_sem_GRAND_TOTAL += 100
    else:
        current_sem_list = None

    current_sem_PERCENTAGE = float(
        (current_sem_TOTAL / current_sem_GRAND_TOTAL)*100) if count_sems != float(0) else None

    return {
        'current_sem_list': current_sem_list,
        'all_sems': all_sems,
        'all_sems_GRAND_TOTAL': all_sems_GRAND_TOTAL,
        'all_sems_PERCENTAGE': all_sems_PERCENTAGE,
        'current_sem_TOTAL': current_sem_TOTAL,
        'current_sem_GRAND_TOTAL': current_sem_GRAND_TOTAL,
        'current_sem_PERCENTAGE': current_sem_PERCENTAGE
    }


@login_required(login_url='login_view')
@allowed_users(['admin'])
def viewuser_admin_view(request, user):
    """
    Returns user data object according to groups assigned.
    """
    user = User.objects.get(username=user)
    try:
        group = user.groups.all()[0].name
        if group == 'student':
            user = get_object_or_404(User, student__user=user)
    except ObjectDoesNotExist:
        user = get_object_or_404(User, teacher__name=user)

    marks = marks_and_percentage(user)

    context = {
        'user': user,
        'current_sem_list': marks['current_sem_list'],
        'all_sems': marks['all_sems'],
        'all_sems_GRAND_TOTAL': marks['all_sems_GRAND_TOTAL'],
        'all_sems_PERCENTAGE': marks['all_sems_PERCENTAGE'],
        'current_sem_TOTAL': marks['current_sem_TOTAL'],
        'current_sem_GRAND_TOTAL': marks['current_sem_GRAND_TOTAL'],
        'current_sem_PERCENTAGE': marks['current_sem_PERCENTAGE']
    }

    return render(request, 'users/details.html', context)


@login_required(login_url='login_view')
@allowed_users(['teacher'])
def viewuser_general_view(request, user):
    """
    Returns user data object according to groups assigned.
    This view is same as viewuser_admin_view but has different url. 
    """
    user = User.objects.get(username=user)
    user = get_object_or_404(User, student__user=user)
    marks = marks_and_percentage(user)

    context = {
        'user': user,
        'current_sem_list': marks['current_sem_list'],
        'all_sems': marks['all_sems'],
        'all_sems_GRAND_TOTAL': marks['all_sems_GRAND_TOTAL'],
        'all_sems_PERCENTAGE': marks['all_sems_PERCENTAGE'],
        'current_sem_TOTAL': marks['current_sem_TOTAL'],
        'current_sem_GRAND_TOTAL': marks['current_sem_GRAND_TOTAL'],
        'current_sem_PERCENTAGE': marks['current_sem_PERCENTAGE']
    }

    return render(request, 'users/details.html', context)
