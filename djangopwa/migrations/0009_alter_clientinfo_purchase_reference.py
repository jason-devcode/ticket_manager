# Generated by Django 5.0.6 on 2024-09-20 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangopwa', '0008_alter_payment_purchase_reference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientinfo',
            name='purchase_reference',
            field=models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Referencia de compra'),
        ),
    ]
