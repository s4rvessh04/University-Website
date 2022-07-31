import django_filters

from .models import *


class AcademicFilter(django_filters.FilterSet):
    class Meta:
        model = Academic
        fields = ['semester', 'subject']

    # Overriding defaults

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super(AcademicFilter, self).__init__(
            data=data, queryset=queryset, request=request, prefix=prefix)
        self.filters['semester'].field.widget.attrs.update(
            {"class": "form-select form-select-lg mb-3", "aria-label": ".form-select-lg example"})
        self.filters['subject'].field.widget.attrs.update(
            {"class": "form-select form-select-lg mb-3", "aria-label": ".form-select-lg example"})


class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = ['branch']

    # Overriding defaults

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super(StudentFilter, self).__init__(
            data=data, queryset=queryset, request=request, prefix=prefix)
        self.filters['branch'].field.widget.attrs.update({'class': 'form-select mb-4 mt-4', 'id': "floatingSelect branch", 'aria-label': "Floating label select example",
                                                          'name': "dropdown_branch", 'onchange': "this.form.submit()"})
