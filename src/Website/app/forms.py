from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import Branch, InternshipApplicant, ApiUser


class CareersInternshipform(forms.ModelForm):
    email = forms.EmailField(max_length=200, label='Email address', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    phone = forms.CharField(max_length=100, label='Contact Number', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    location = forms.CharField(max_length=200, label='Location', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    qualificationAndqueries = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'floatingTextarea2', 'style': 'height:100px', 'placeholder': 'Name'}))

    class Meta:
        model = InternshipApplicant
        fields = '__all__'


class CreateUserForm(UserCreationForm):
    username = forms.CharField(max_length=120, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    name = forms.CharField(max_length=120, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Name'}))
    email = forms.EmailField(label='Email address', max_length=75, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Phone'}))
    password1 = forms.CharField(max_length=120, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=120, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Confirm Password'}))
    is_teacher = forms.BooleanField(required=False, label='Teacher', widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input', 'id': 'flexCheckDefault', 'value': False}))
    choices_branch = [(branch, branch)for branch in Branch.objects.all()]
    # added the defualt option if the user type is not student
    choices_branch.insert(0, ('None', '-------'))
    branch = forms.ChoiceField(required=False, choices=choices_branch,
                               initial='None', widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'phone',
                  'branch', 'is_teacher', 'password1', 'password2']


class UpdateUserDetails(forms.ModelForm):
    username = forms.CharField(max_length=120, label='Change Username', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Enter new username'}))
    password = forms.CharField(max_length=120, label='Change Password', required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Enter new password'}))

    class Meta:
        model = User
        fields = ['username', 'password']


class ApiUserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email address', max_length=75, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Email'}))

    class Meta:
        model = ApiUser
        fields = ['email']
