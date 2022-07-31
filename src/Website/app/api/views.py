# REST imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from app.models import Academic, Student, User, InternshipApplicant, Teacher
from .serializers import TokenSerializer, AcademicSerializer, StudentSerializer, AllAcademicSerializer, UsersSerializer, InternshipApplicantSerializer


# USER

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_links_view(request, format=None):
    """
    Returns a python dictionary of user accessible links.
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'detail': 'User verification unsuccessful.'}, status=status.HTTP_401_UNAUTHORIZED)

    links = {
        'my-links': reverse('api:links', request=request, format=format),
        'account-details': reverse('api:user-details', request=request, args=[request.user.id], format=format),
        'my-student-profile': reverse('api:student-details', request=request, args=[student.id], format=format),
        'my-academics': reverse('api:academics-details', request=request, format=format),
        'academics-list': reverse('api:academics-list', request=request, format=format),
    }

    return Response(links)


def verify_current_and_accessing_user(request, pk):
    """
    Verifying user accessing data.
    """
    if request.user.id == pk or request.user.is_staff:
        return True
    else:
        return False


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_user_details_view(request, pk):
    """
    Returns user realted information upon successful verification,
    else throws error.
    """
    if verify_current_and_accessing_user(request, pk):
        user = User.objects.get(id=pk)
        serializer = UsersSerializer(user, context={'request': request})
        return Response(serializer.data)
    else:
        return Response({'detail': 'Not authorized to view this data.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_user_token_view(request, pk):
    """
    Returns user's token information upon successful verification,
    else throws error.
    """
    if verify_current_and_accessing_user(request, pk):
        token = Token.objects.get(user_id=pk)
        serializer = TokenSerializer(token, context={'request': request})
        return Response(serializer.data)
    else:
        return Response({'detail': 'Not authorized to view this data.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def api_student_details_view(request, pk):
    """
    Returns student's self information.
    """
    try:
        user = User.objects.get(student__id=pk)
    except User.DoesNotExist:
        return Response({'Error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.id == user.id or request.user.is_staff:
        student = Student.objects.get(id=pk)
        serializer = StudentSerializer(student, context={'request': request})
        return Response(serializer.data)
    else:
        return Response({'detail': 'Not authorized to view this data'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def api_academic_view(request):
    try:
        academic = Academic.objects.all()
    except Academic.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AcademicSerializer(academic)
    return Response(serializer.data)


class Api_academic_view(ListAPIView):
    """
    Returns acdemic details about the student accessing this data. 
    """
    serializer_class = AcademicSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self, *args, **kwargs):
        try:
            queryset_list = Academic.objects.filter(
                student__user=self.request.user)
        except Academic.DoesNotExist:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        return queryset_list


class Api_academic_list_view(ListAPIView):
    """
    Returns all the academic data.
    And also has a feature to sort the data with correct parameters/fields.
    """
    serializer_class = AcademicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student__name', 'subject__name', 'semester__name']
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get_queryset(self, *args, **kwargs):
        queryset_list = Academic.objects.all()
        return queryset_list


# ADMIN
# Admin related view will have different sets of url(other than USER's),
# which will return all the data according to the url being accessed,
# along with the hyperlinks for easy data querying.

# Check serializers.py for hyperlinked fields.

@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_links_admin_view(request, format=None):
    links = {
        'links-list': reverse('links-list', request=request, format=format),
        'all-users': reverse('all-users', request=request, format=format),
        'student-list': reverse('student-list', request=request, format=format),
        'academic-list': reverse('academic-list', request=request, format=format),
        'internship-applicant-list': reverse('internship-applicant-list', request=request, format=format),
    }

    return Response(links)


class Api_allusers_view(ListAPIView):
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination
    PageNumberPagination.page_size = 10
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['id']
    ordering = 'id'
    permission_classes = [BasicAuthentication, IsAdminUser]

    def get_queryset(self, *args, **kwargs):
        queryset_list = User.objects.all()
        query = self.request.GET.get('q')

        if query:
            queryset_list = queryset_list.filter(
                Q(username__icontains=query) | Q(email__icontains=query))
        return queryset_list


class Api_students_view(ListAPIView):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__username', 'name', 'branch__name']
    permission_classes = [IsAdminUser]

    def get_queryset(self, *args, **kwargs):
        queryset_list = Student.objects.all()
        return queryset_list


class Api_admin_academic_view(ListAPIView):
    serializer_class = AllAcademicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'student__name', 'student__user__username', 'subject__name', 'semester__name']
    permission_classes = [IsAdminUser]

    def get_queryset(self, *args, **kwargs):
        queryset_list = Academic.objects.all()
        return queryset_list


class Api_internship_applicant_view(ListAPIView):
    serializer_class = InternshipApplicantSerializer
    filter_backends = [SearchFilter]
    search_fields = ['email']
    permission_classes = [IsAdminUser]

    def get_queryset(self, *args, **kwargs):
        queryset_list = InternshipApplicant.objects.all()
        query = self.request.GET.get('q')

        if query:
            queryset_list = queryset_list.filter(Q(email__icontains=query))
        return queryset_list