# Generated by Django 4.0.4 on 2022-04-26 16:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variation',
            old_name='variaton_value',
            new_name='variation_value',
        ),
    ]