from datetime import datetime

from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet

from config import settings
from .permissions import IsOwnerOrSuperuser
from .serializers import RegisterSerializer, ProfileSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from random import randint
from .models import PasswordReset, CustomUser
from django.core.mail import send_mail


# Create your views here.


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()


@api_view(['POST'])
def change_password(request):
    old_password = request.data['old_password']
    new_password = request.data['new_password']

    if request.method == 'POST':

        if not old_password or not new_password:
            return Response(data={'message': 'Old password and new password are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if user.check_password(old_password):

            try:
                validate_password(new_password)
            except Exception as e:
                return Response(data={'message': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response(data={'message': 'Password successfully changed'},
                            status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'Old password do not match'},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={'message': 'Only POST method allowed'},
                        status=status.HTTP_400_BAD_REQUEST
                        )


@api_view(['POST', 'GET'])
def reset_password(request):
    if request.method == 'POST':
        reset_code = request.data['code']
        new_password = request.data['new_password']
        try:
            reset_user = PasswordReset.objects.get(reset_code=reset_code, status=True)
            if datetime.now().timestamp() - reset_user.created_at.timestamp() > 180:
                return Response(
                    data={'message': 'fail', 'description': 'The code has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(data={'message': 'fail', 'description': 'Code invalid'})
        try:
            user = get_user_model().objects.get(pk=int(reset_user.user.id))
            PasswordReset.objects.filter(reset_code=reset_code).update(status=False)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password successfully reset'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'fail', 'description':f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        email = request.data['email']
        user = get_user_model().objects.filter(email=email).first()
        if user:
            reset_code = f'{randint(100, 999)}-{randint(100, 999)}'
            try:
                reset_request = PasswordReset.objects.create(user=user, reset_code=reset_code)
                reset_request.save()
                send_mail(
                    subject='Password Reset Request',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    message=f'Insert this code to reset your password: {reset_code} \n\n'
                            f'Code will expire in 3 minutes'
                )
                return Response(
                    data={'message': 'We just sent a code to your email as your request.Check your email, please'},
                    status=status.HTTP_200_OK
                )
            except Exception:
                return Response(
                    data={'message': 'fail'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                data={'message': 'fail', 'description': 'Email not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(data={'message': 'Method should be GET'})


class ProfileViewSet(ModelViewSet):
    http_method_names = ['put', 'patch', 'delete', 'get']
    queryset = CustomUser.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrSuperuser]
