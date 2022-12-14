# Generated by Django 3.2 on 2022-10-04 22:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_auto_20221005_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('На сайте', 'На сайте'), ('При получении', 'При получении')], db_index=True, max_length=100, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Выполнен', 'Выполнен'), ('Курьер выехал', 'Курьер выехал'), ('Готовится', 'Готовится'), ('Принят', 'Принят')], db_index=True, default='Принят', max_length=100, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
    ]
