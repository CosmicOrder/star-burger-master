# Generated by Django 3.2 on 2022-10-01 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_auto_20221001_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарии'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Принят', 'Принят'), ('Курьер выехал', 'Курьер выехал'), ('Готовится', 'Готовится'), ('Выполнен', 'Выполнен')], db_index=True, default='Принят', max_length=100, verbose_name='Статус заказа'),
        ),
    ]
