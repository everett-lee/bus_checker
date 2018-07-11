from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import is_safe_url
from django.views.generic import TemplateView, DeleteView
from django.urls import reverse_lazy
from route_checker.services import get_bus
from .forms import UserAdminCreationForm, LoginForm, BusForm
from .models import BusUser, Buses
from decouple import config
import requests

google_auth_key = {'google_auth_key': config('google_auth_key')}
tfl_auth_key = config('tfl_auth_key')
head = {'Authorisation': tfl_auth_key}

User = get_user_model()
def register_page(request):
    form = UserAdminCreationForm(request.POST or None)
    context = {
        'form': form
    }
    if form.is_valid():
        form.save()
        return redirect('homepage')

    return render(request, 'register.html', context)

@login_required
def manage(request):
    form = BusForm(request.POST or None)
    if request.user.is_anonymous:
        buses = None
    else:
        buses = Buses.objects.filter(user__email=request.user.email)
    context = {
        'form': form,
        'buses': buses
    }
    if form.is_valid():
        form = form.save(commit = False)
        form.user = request.user
        form.save()

    return render(request, 'manage.html', context)

class DeleteBus(DeleteView):
    template_name = 'buses_confirm_delete.html'
    model = Buses
    success_url = reverse_lazy('manage')


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username  = form.cleaned_data.get('username')
        password  = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('homepage')
        else:
            # Return an 'invalid login' error message.
            print('Error')

    return render(request, 'login.html', context)


def log_out(request):
    logout(request)
    return render(request, 'home.html', {})

class BusPage(TemplateView):
    def get(self,request):
        bus = ''
        data = {}

        if 'bus' in request.GET:
                bus = request.GET['bus']
                data = get_bus(bus)

        return render(request, 'home.html', {'data': data, 'google_auth_key': google_auth_key})
