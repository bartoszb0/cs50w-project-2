# Generated by Django 5.1.6 on 2025-03-06 21:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auction_starting_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='starting_price',
        ),
        migrations.AlterField(
            model_name='auction',
            name='highest_bid',
            field=models.DecimalField(decimal_places=2, default=0.01, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.AlterField(
            model_name='bid',
            name='bid',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
