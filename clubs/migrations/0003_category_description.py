# Generated by Django 5.1.5 on 2025-03-24 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0002_alter_bookclub_name_membership"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="description",
            field=models.TextField(default="No description availible"),
        ),
    ]
