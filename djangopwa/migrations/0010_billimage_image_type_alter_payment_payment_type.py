# Generated by Django 5.0.6 on 2024-09-20 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangopwa', '0009_alter_clientinfo_purchase_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='billimage',
            name='image_type',
            field=models.CharField(choices=[('ABONO', 'Abono'), ('CERTIFICATE', 'Certificada')], default='ABONO', max_length=11, verbose_name='Tipo de plantilla'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('BONO1', 'Abono 1'), ('BONO2', 'Abono 2'), ('BONO3', 'Abono 3')], max_length=5, verbose_name='Tipo de Pago'),
        ),
    ]
