from django.urls import path
from .views import SignUp,  LogoutUser, UserResetPassword, UserResetPasswordDone,\
    UserResetPasswordConfirm, UserResetPasswordComplete, UserLogin, UserPasswordChange, \
    UserPasswordChangeDone

urlpatterns = [
    path('register', SignUp.as_view(), name='signup'),
    path('login', UserLogin.as_view(), name='login'),
    path('logout', LogoutUser.as_view(), name='logout'),
    path('password_change', UserPasswordChange.as_view(), name='password-change'),
    path('password_change/done', UserPasswordChangeDone.as_view(), name='password-change-done'),
    path('password-reset', UserResetPassword.as_view(), name='password-reset'),
    path('password-reset/done', UserResetPasswordDone.as_view(), name='password-reset-done'),
    path('password-reset/confirm/<uidb64>/<token>/', UserResetPasswordConfirm.as_view(),
         name='password-reset-confirm'),
    path('password-reset/complete', UserResetPasswordComplete.as_view(), name='password-reset-complete'),

]
