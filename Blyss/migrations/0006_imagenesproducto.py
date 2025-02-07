# Generated by Django 5.0.9 on 2025-01-27 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0005_categoriasproductos_subcategoriasproductos'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagenesProducto',
            fields=[
                ('IdImagen', models.AutoField(primary_key=True, serialize=False)),
                ('Imagen', models.BinaryField()),
                ('EsPrincipal', models.BooleanField(default=False)),
                ('FechaAgregado', models.DateTimeField(auto_now_add=True)),
                ('IdProducto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='Blyss.productos')),
            ],
        ),
    ]
