# Generated by Django 5.0.6 on 2024-09-20 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangopwa', '0010_billimage_image_type_alter_payment_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billimage',
            name='image_type',
            field=models.CharField(choices=[('TICKET_TEMPLATE', 'Plantilla de boleta'), ('CERTIFICATE_TEMPLATE', 'Plantilla de Certificado')], default='TICKET_TEMPLATE', max_length=20, verbose_name='Tipo de plantilla'),
        ),
    ]
