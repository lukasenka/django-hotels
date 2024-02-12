# Generated by Django 4.1.1 on 2023-01-21 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viesbuciai', '0007_alter_profile_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='user',
        ),
        migrations.AddField(
            model_name='client',
            name='password',
            field=models.CharField(default='test', max_length=20, verbose_name='Slaptazodis'),
        ),
        migrations.AddField(
            model_name='client',
            name='username',
            field=models.CharField(default=1, max_length=15, verbose_name='Slapyvardis'),
            preserve_default=False,
        ),
    ]