# Generated by Django 5.0.7 on 2024-07-23 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_alter_group_scientific_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
