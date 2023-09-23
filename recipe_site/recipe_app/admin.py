from django.contrib import admin
from .models import *


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'preparation_time', 'servings', 'difficulty_level', 'category', 'recipe_image', 'author', 'date_created', 'publish']
    list_editable = ['publish']
    list_filter = ['category', 'difficulty_level', 'publish']


class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ['name']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']   


class CommentAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'author', 'text', 'date_created']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(DifficultyLevel, DifficultyLevelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)