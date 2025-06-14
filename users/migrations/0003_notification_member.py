# Generated by Django 5.1.5 on 2025-06-03 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0011_bookclub_created_at"),
        ("users", "0002_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="member",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="clubs.membership",
            ),
        ),
    ]
