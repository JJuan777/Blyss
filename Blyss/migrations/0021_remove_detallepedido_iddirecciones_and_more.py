# Generated by Django 5.0.9 on 2025-02-11 23:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0020_detallepedido_iddirecciones'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallepedido',
            name='IdDirecciones',
        ),
        migrations.AddField(
            model_name='pedido',
            name='IdDirecciones',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pedidos_envio', to='Blyss.direcciones'),
        ),
    ]
