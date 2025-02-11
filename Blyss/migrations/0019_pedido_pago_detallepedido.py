# Generated by Django 5.0.9 on 2025-02-11 22:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0018_direcciones_direccionesusuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('IdPedido', models.AutoField(primary_key=True, serialize=False)),
                ('Estado', models.CharField(max_length=50)),
                ('FechaPedido', models.DateTimeField(auto_now_add=True)),
                ('Total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IdUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('IdPago', models.AutoField(primary_key=True, serialize=False)),
                ('Metodo', models.CharField(max_length=50)),
                ('FechaPago', models.DateTimeField(auto_now_add=True)),
                ('Monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('TransaccionId', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('IdPedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='Blyss.pedido')),
            ],
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('IdDetalle', models.AutoField(primary_key=True, serialize=False)),
                ('Cantidad', models.PositiveIntegerField()),
                ('PrecioUnitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IdProducto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles_pedido', to='Blyss.productos')),
                ('IdPedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='Blyss.pedido')),
            ],
        ),
    ]
