from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from accounts.mixins import RoleRequiredMixin
from accounts.models import User

from .forms import ProfileForm, SchoolProfileForm, UserEditForm
from .models import SchoolProfile


class DirectionOnly(RoleRequiredMixin):
    allowed_roles = [User.Role.DIRECTION]


class SettingsHome(DirectionOnly, TemplateView):
    template_name = 'school_settings/home.html'


class SchoolProfileView(DirectionOnly, UpdateView):
    form_class = SchoolProfileForm
    template_name = 'school_settings/form.html'
    success_url = reverse_lazy('settings_home')

    def get_object(self, queryset=None):
        return SchoolProfile.get()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'School information'
        context['back_url'] = reverse('settings_home')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'School information saved.')
        return super().form_valid(form)


class UserList(DirectionOnly, ListView):
    template_name = 'school_settings/user_list.html'
    paginate_by = 20
    context_object_name = 'users'

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False).order_by('role', 'last_name', 'first_name', 'username')
        q = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '')
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(first_name__icontains=q)
                | Q(last_name__icontains=q) | Q(email__icontains=q)
            )
        if role in User.Role.values:
            qs = qs.filter(role=role)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['role'] = self.request.GET.get('role', '')
        context['roles'] = User.Role.choices
        return context


class UserEdit(DirectionOnly, UpdateView):
    template_name = 'school_settings/form.html'
    form_class = UserEditForm
    success_url = reverse_lazy('user_list')

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editing_self'] = self.object.pk == self.request.user.pk
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit user: %s' % self.object.username
        context['back_url'] = reverse('user_list')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'User saved.')
        return super().form_valid(form)


class UserPasswordReset(DirectionOnly, FormView):
    template_name = 'school_settings/form.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return super().test_func() and self.kwargs['pk'] != self.request.user.pk

    def get_target(self):
        return get_object_or_404(User.objects.filter(is_superuser=False), pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_target()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target = self.get_target()
        context['title'] = 'Reset password: %s' % target.username
        context['back_url'] = reverse('user_list')
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The password was changed. Give the new password to the user.')
        return super().form_valid(form)


@login_required
def my_account(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your details were saved.')
        return redirect('my_account')
    return render(request, 'school_settings/my_account.html', {'form': form})


class MyPasswordChange(PasswordChangeView):
    template_name = 'school_settings/form.html'
    success_url = reverse_lazy('my_account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change my password'
        context['back_url'] = reverse('my_account')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your password was changed.')
        return super().form_valid(form)