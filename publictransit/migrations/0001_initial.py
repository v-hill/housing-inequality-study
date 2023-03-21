# Generated by Django 4.1.7 on 2023-03-20 21:54

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latitude", models.DecimalField(decimal_places=5, max_digits=7)),
                ("longitude", models.DecimalField(decimal_places=5, max_digits=7)),
            ],
        ),
    ]
