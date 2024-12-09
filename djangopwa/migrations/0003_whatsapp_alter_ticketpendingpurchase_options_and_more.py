# Generated by Django 5.0.6 on 2024-08-18 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangopwa', '0002_ticketpendingpurchase'),
    ]

    operations = [
        migrations.CreateModel(
            name='Whatsapp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('whatsapp', models.CharField(default='', max_length=32, verbose_name='Whatsapp')),
            ],
            options={
                'verbose_name': 'Whatsapp',
                'verbose_name_plural': 'Whatsapp',
            },
        ),
        migrations.AlterModelOptions(
            name='ticketpendingpurchase',
            options={'verbose_name': 'Compra Pendiente', 'verbose_name_plural': 'Compras Pendientes'},
        ),
        migrations.AlterField(
            model_name='clientinfo',
            name='city',
            field=models.CharField(max_length=32, verbose_name='Ciudad'),
        ),
        migrations.AlterField(
            model_name='clientinfo',
            name='document_number',
            field=models.IntegerField(verbose_name='Documento'),
        ),
        migrations.AlterField(
            model_name='clientinfo',
            name='telephone',
            field=models.IntegerField(verbose_name='Telefono'),
        ),
    ]
