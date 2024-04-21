from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest

from .models import *
from .forms import  *
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import ListView, CreateView, FormView
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum


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
        recipe_list = context[self.context_object_name]
        add_ratings_to_recipes(recipe_list)
        context[self.context_object_name] = recipe_list
        stars = [1, 2, 3, 4, 5]
        context['stars'] = stars
        print(context)
        return context

    

class RecipeSearchListView(ListView):
    model = Recipe
    template_name = 'search_results.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            query_lower = query.lower()  # Переведення пошукового запиту в нижній регістр
            matching_recipes = Recipe.objects.filter(title__icontains=query_lower)
            if not matching_recipes:
                matching_recipes = Recipe.objects.filter(title__icontains=query_lower.capitalize())
                if not matching_recipes:
                    words = query_lower.split()
                    for word in words:
                        matching_recipes |= Recipe.objects.filter(title__icontains=word)
                        if matching_recipes.count() >= 5:
                            break
            return matching_recipes
        return Recipe.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_list = context[self.context_object_name]
        add_ratings_to_recipes(recipe_list)
        context[self.context_object_name] = recipe_list
        stars = [1, 2, 3, 4, 5]
        context['stars'] = stars
        print(context)
        return context
    


class AllRecipe(ListView):
    model = Recipe
    template_name = 'all_recipe.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_list = context[self.context_object_name]

        add_ratings_to_recipes(recipe_list)  
        context[self.context_object_name] = recipe_list
        stars = [1, 2, 3, 4, 5]
        context['stars'] = stars
        print(context)
        return context

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
    template_name = 'recipe_detail.html'

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comments = recipe.comment_set.all().order_by('-date_created')
        form = CommentForm()
        rating_form = RatingForm()

        is_favorite = False  # Початково рецепт не улюблений

        # Логіка для обчислення середнього рейтингу
        average_rating, total_reviews, rating_residue = calculate_average_rating(recipe)

        if request.user.is_authenticated:
            if FavoriteRecipe.objects.filter(recipe=recipe, user=request.user).exists():
                is_favorite = True

        return render(request, self.template_name, {
            'recipe': recipe,
            'comments': comments,
            'form': form,
            'rating_form': rating_form,  # Додано форму оцінки
            'is_favorite': is_favorite,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'rating_residue': rating_residue,
            'stars': [1,2,3,4,5],
        })

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comments = recipe.comment_set.all()
        form = CommentForm(request.POST)
        rating_form = RatingForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', recipe_id=recipe_id)

        if rating_form.is_valid():
            rating = rating_form.cleaned_data['rating']

            existing_rating, created = Rating.objects.get_or_create(recipe=recipe, user=request.user, defaults={'rating_value': rating})

            if not created:
                existing_rating.rating_value = rating
                existing_rating.save()

            total_reviews = Rating.objects.filter(recipe=recipe).count()
            total_rating = Rating.objects.filter(recipe=recipe).aggregate(Sum('rating_value'))['rating_value__sum']
            average_rating = round(total_rating / total_reviews, 2) if total_reviews > 0 else 0
            rating_residue = average_rating % 1

            # Повертаємо JsonResponse замість redirect
            return JsonResponse({'average_rating': average_rating, 'total_reviews': total_reviews, 'rating_residue': rating_residue})

        return render(request, self.template_name, {
            'recipe': recipe,
            'comments': comments,
            'form': form,
            'rating_form': rating_form,
        })
    

def calculate_average_rating(recipe):
    reviews = Rating.objects.filter(recipe=recipe)
    total_reviews = reviews.count()
    if total_reviews > 0:
        total_rating = sum(review.rating_value for review in reviews)
        average_rating = round(total_rating / total_reviews, 2)
        rating_residue = average_rating % 1
    else:
        average_rating = 0
        rating_residue = 0
    return average_rating, total_reviews, rating_residue


def add_ratings_to_recipes(recipes):
    for recipe in recipes:
        average_rating, total_reviews, rating_residue = calculate_average_rating(recipe)
        recipe.average_rating = average_rating
        recipe.total_reviews = total_reviews
        recipe.rating_residue = rating_residue


def rate_recipe(request, recipe_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        rating = int(request.POST.get('rating', 0))
        
        if 1 <= rating <= 5:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            user = request.user

            existing_rating, created = Rating.objects.get_or_create(recipe=recipe, user=user, defaults={'rating_value': rating})

            if not created:
                existing_rating.rating_value = rating
                existing_rating.save()

            total_reviews = Rating.objects.filter(recipe=recipe).count()
            total_rating = Rating.objects.filter(recipe=recipe).aggregate(Sum('rating_value'))['rating_value__sum']
            average_rating = round(total_rating / total_reviews, 2) if total_reviews > 0 else 0
            rating_residue = average_rating % 1

            return JsonResponse({'average_rating': average_rating, 'total_reviews': total_reviews, 'rating_residue': rating_residue})
        else:
            return JsonResponse({'error': 'Invalid rating value'})
    else:
        return JsonResponse({'error': 'Invalid request'})


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
            add_ratings_to_recipes(recipes)
            return render(request, self.template_name, {'favorite_recipes': favorite_recipes, 'recipes': recipes, 'stars': [1,2,3,4,5]})
        else:
            return render(request, 'not_authenticated.html')
        


class UserRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'user_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 10

    def get_queryset(self):
        recipes = Recipe.objects.filter(author=self.request.user)
        add_ratings_to_recipes(recipes)
        return recipes
