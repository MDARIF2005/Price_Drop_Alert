# Generated by Django 5.1 on 2024-12-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PriceTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_link', models.URLField(max_length=500)),
                ('target_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('email', models.EmailField(max_length=254)),
                ('progress', models.CharField(default='incomplete', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
