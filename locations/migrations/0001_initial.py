# Generated by Django 3.2 on 2022-08-28 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, verbose_name='адрес')),
                ('lat', models.FloatField(verbose_name='широта')),
                ('lon', models.FloatField(verbose_name='долгота')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'unique_together': {('lat', 'lon')},
            },
        ),
    ]
