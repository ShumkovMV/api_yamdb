# Generated by Django 3.2 on 2024-11-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, default='', max_length=2000, null=True, verbose_name='Биография'),
        ),
    ]
