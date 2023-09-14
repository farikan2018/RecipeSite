from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import *
from .forms import TankForm, RegisterForm, LoginForm, KlasForm, StranaForm
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, FormView
from django.contrib.auth import login, logout
from django.contrib import messages


class HomeTank(ListView):
    model = Tank
    template_name = 'firstapp/index.html'
    context_object_name = 'tanks'
    paginate_by = 5

    def get_queryset(self):
        return Tank.objects.filter(publish=True)