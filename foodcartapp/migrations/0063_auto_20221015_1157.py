# Generated by Django 3.2 on 2022-10-15 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0062_auto_20221005_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('На сайте', 'На сайте'), ('Способ оплаты не выбран', 'Способ оплаты не выбран'), ('При получении', 'При получении')], db_index=True, default='Способ оплаты не выбран', max_length=100, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Принят', 'Принят'), ('Выполнен', 'Выполнен'), ('Готовится', 'Готовится'), ('Курьер выехал', 'Курьер выехал')], db_index=True, default='Принят', max_length=100, verbose_name='Статус заказа'),
        ),
    ]
