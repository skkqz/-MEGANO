from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import views as aut_view
from .forms import CustomUserCreationForm


class SignUp(CreateView):
    """Класс представления Регистрации пользователя"""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'


class LogoutUser(aut_view.LogoutView):
    """Класс представления Выхода пользователя из системы"""
    next_page = '/'


class UserResetPassword(aut_view.PasswordResetView):
    """Класс представления Формы востановления пароля"""
    template_name = 'users/password_reset_form.html'
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy('password-reset-done')


class UserResetPasswordDone(aut_view.PasswordResetDoneView):
    """Класс представления Отправки письма с сылкой на смену пароля"""
    template_name = "users/password_reset_done.html"
    title = "Password reset sent"


class UserResetPasswordConfirm(aut_view.PasswordResetConfirmView):
    """Класс представления Ввод нового пароля """
    template_name = 'users/password_reset_confirm.html'
    post_reset_login = True
    success_url = reverse_lazy('login')


class UserResetPasswordComplete(aut_view.PasswordResetCompleteView):
    """Класс представления О завершении изменения пароля"""
    template_name = 'users/password_reset_complete.html'


class UserLogin(aut_view.LoginView):
    """Класс представления на страницу входа пользователя"""
    template_name = 'users/login.html'


class UserPasswordChange(aut_view.PasswordChangeView):
    """Класс представления Смена пароля"""
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('password-change-done')


class UserPasswordChangeDone(aut_view.PasswordChangeDoneView):
    """Класс представления Пароль изменен"""
    template_name = 'users/password_change_done.html'
