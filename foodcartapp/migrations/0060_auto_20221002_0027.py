# Generated by Django 3.2 on 2022-10-01 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_auto_20221001_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('При получении', 'При получении'), ('На сайте', 'На сайте')], db_index=True, max_length=100, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Курьер выехал', 'Курьер выехал'), ('Готовится', 'Готовится'), ('Выполнен', 'Выполнен'), ('Принят', 'Принят')], db_index=True, default='Принят', max_length=100, verbose_name='Статус заказа'),
        ),
    ]
