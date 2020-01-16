# Generated by Django 3.0.2 on 2020-01-16 16:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.WAFFLE_FLAG_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FlagMember",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        help_text="Date on which to add user to Flag group."
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        help_text="Date on which to remove user from Flag group."
                    ),
                ),
                ("created_at", models.DateTimeField()),
                (
                    "flag",
                    models.ForeignKey(
                        help_text="Waffle flag to add the user to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to=settings.WAFFLE_FLAG_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User to add to waffle flag group.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]
