# Generated by Django 5.1.5 on 2025-06-02 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0005_bookclub_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookclub",
            name="location",
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
    ]
