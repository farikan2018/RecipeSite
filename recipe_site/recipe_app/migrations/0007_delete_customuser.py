# Generated by Django 4.2.5 on 2023-09-23 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0006_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
