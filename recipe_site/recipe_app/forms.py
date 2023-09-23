from django import forms
from .models import *
from django.forms import ModelForm, TextInput, Textarea, Select, ClearableFileInput, EmailInput, NumberInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# from captcha.fields import CaptchaField


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='', widget=(TextInput({"class": "form-control", "placeholder": "Введіть нік користувача"})))
    password = forms.CharField(label='', widget=(TextInput({"class": "form-control", "placeholder": "Введіть пароль"})))


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='', widget=(TextInput({"class": "form-control", "placeholder": "Введіть нік користувача"})))
    email = forms.EmailField(label='', widget=(EmailInput({"class": "form-control", "placeholder": "Введіть ваш email"})))
    password1 = forms.CharField(label='', widget=(TextInput({"class": "form-control", "placeholder": "Введіть пароль"})))
    password2 = forms.CharField(label='', widget=(TextInput({"class": "form-control", "placeholder": "Повторіть пароль"})))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Цей нікнейм вже використовується. Будь ласка, виберіть інший.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ця електронна пошта вже використовується. Будь ласка, введіть іншу.")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'ingredients', 'instructions', 'instructions', 'preparation_time', 'servings', 'difficulty_level', 'category', 'recipe_image']
        widgets = {
            'title': TextInput({
                "class": "form-control",
                "placeholder": "Введіть наву страви"
            }),
            'ingredients': Textarea({
                "class": "form-control",
                "placeholder": "Введіть всі необхідні інгрідієнти"
            }),
            'instructions': Textarea({
                "class": "form-control",
                "placeholder": "Напишіть інструкцію приготування"
            }),
            'preparation_time': TextInput({
                "class": "form-control",
                "placeholder": "Напишіть скільки часу готується страва"
            }),
            'servings': NumberInput({
                "class": "form-control",
                "placeholder": "Напишіть скільки вийде порцій"
            }),
            'difficulty_level': Select({
                "class": "form-control"
            }),
            'category': Select({
                "class": "form-control"
            }),
            'recipe_image': ClearableFileInput({
                "class": "form-control",
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

