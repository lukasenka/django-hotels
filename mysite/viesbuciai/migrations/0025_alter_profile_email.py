# Generated by Django 4.1.1 on 2023-01-27 19:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viesbuciai', '0024_alter_order_admin_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.CharField(blank=True, db_column='email', db_index=True, max_length=30, null=True, validators=[django.core.validators.EmailValidator()], verbose_name='Email'),
        ),
    ]
