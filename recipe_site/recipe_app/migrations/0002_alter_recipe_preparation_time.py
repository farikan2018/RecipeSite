# Generated by Django 4.2.5 on 2023-09-14 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='preparation_time',
            field=models.TextField(verbose_name='Час готування'),
        ),
    ]