from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext as _

# Модель для складності рецепту
class DifficultyLevel(models.Model):
    name = models.CharField('Рівень складності приготування', max_length=20)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Рівень складності приготування'
        verbose_name_plural = 'Рівні складності приготування'

# Модель для категорій рецептів
class Category(models.Model):
    name = models.CharField('Назва категорії',max_length=100)
    category_image = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото страви', blank=True, null=True,)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

# Модель для рецептів
class Recipe(models.Model):
    title = models.CharField('Назва страви', max_length=200)
    ingredients = models.TextField('Інгрідієнти')
    instructions = models.TextField('Інструкція')
    preparation_time = models.TextField('Час готування')
    servings = models.PositiveIntegerField('Кількість порцій')
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, verbose_name='Складність приготування')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категорія страви')
    recipe_image = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото страви', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField('Дата створення допису', auto_now_add=True)
    publish = models.BooleanField('Опубліковано', default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепти'
        ordering = ['-id']

# Модель для коментарів
class Comment(models.Model):
    text = models.TextField('Текст коментаря')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор коментаря')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт під яким залишили коментар')
    date_created = models.DateTimeField('Дата створення коментаря', auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.recipe.title}'
    
    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

# Модель для оцінок рецептів
class Rating(models.Model):
    rating_value = models.PositiveIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.rating_value} stars for {self.recipe.title} by {self.user.username}'
    
    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

# Модель для обраних рецептів користувачів
class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} added {self.recipe.title} to favorites'
    
