from django.urls import path
from .views import *



urlpatterns = [
    path('', HomeRecipe.as_view(), name='home'),
    path('all_recipe/', AllRecipe.as_view(), name='all_recipe'),
    path('category/<int:category_id>/', CategoryRecipesView.as_view(), name='category_recipes'),
    path('search/', RecipeSearchListView.as_view(), name='search_recipes'),
    path('regist/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('recipe/<int:recipe_id>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('create_recipe/', create_recipe, name='create_recipe'),
    path('recipe/<int:recipe_id>/toggle_favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorite_recipes/', FavoriteRecipesView.as_view(), name='favorite_recipes'),
]