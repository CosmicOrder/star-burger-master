# Generated by Django 3.2 on 2022-09-16 21:51

from django.db import migrations


def replace_none_with_empty_string(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for order in Order.objects.all():
        order.comment = ''
        order.save()


def move_backward(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for order in Order.objects.all():
        order.comment = None
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_auto_20220910_2255'),
    ]

    operations = [
        migrations.RunPython(replace_none_with_empty_string, move_backward)
    ]
