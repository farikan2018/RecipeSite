from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse

from .models import *
from .forms import  *
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import ListView, CreateView, FormView
from django.contrib.auth import login, logout
from django.contrib import messages


class HomeRecipe(ListView):
    model = Category
    template_name = 'index.html'
    context_object_name = 'categories'



class CategoryRecipesView(ListView):
    model = Recipe
    template_name = 'all_recipe.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Recipe.objects.filter(category_id=category_id, publish=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context
    

class RecipeSearchListView(ListView):
    model = Recipe
    template_name = 'search_results.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Recipe.objects.filter(title__icontains=query)
        return Recipe.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context    


class AllRecipe(ListView):
    model = Recipe
    template_name = 'all_recipe.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_queryset(self):
        return Recipe.objects.filter(publish=True)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ви успішно зареєструвались')
            return redirect('home')
        else:
            messages.error(request, 'Проблема під час реєстрації')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


class RecipeDetailView(View):
    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comments = recipe.comment_set.all().order_by('-date_created')
        form = CommentForm()
        is_favorite = False  # Початково рецепт не улюблений

        if request.user.is_authenticated:
            # Перевірте, чи рецепт улюблений користувачем
            if FavoriteRecipe.objects.filter(recipe=recipe, user=request.user).exists():
                is_favorite = True

        return render(request, 'recipe_detail.html', {'recipe': recipe, 'comments': comments, 'form': form, 'is_favorite': is_favorite})

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comments = recipe.comment_set.all()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', recipe_id=recipe_id)

        return render(request, 'recipe_detail.html', {'recipe': recipe, 'comments': comments, 'form': form})
    

def toggle_favorite(request, recipe_id):
    if request.user.is_authenticated:
        recipe = Recipe.objects.get(pk=recipe_id)
        user = request.user
        favorite, created = FavoriteRecipe.objects.get_or_create(user=user, recipe=recipe)
        if created:
            message = "Рецепт додано до улюблених."
        else:
            favorite.delete()
            message = "Рецепт видалено з улюблених."
        return JsonResponse({'message': message})
    else:
        return JsonResponse({'message': 'Потрібно увійти в систему, щоб додавати рецепти до улюблених.'})   


def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('home')
    else:
        form = RecipeForm()
    
    return render(request, 'create_recipe.html', {'form': form})


class FavoriteRecipesView(View):
    template_name = 'favorite_recipes.html'

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            favorite_recipes = FavoriteRecipe.objects.filter(user=user)
            # Отримання списку рецептів, які є улюбленими для даного користувача
            recipes = [fav.recipe for fav in favorite_recipes]
            return render(request, self.template_name, {'favorite_recipes': favorite_recipes, 'recipes': recipes})
        else:
            return render(request, 'not_authenticated.html')
