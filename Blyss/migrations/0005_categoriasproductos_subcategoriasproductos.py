# Generated by Django 5.0.9 on 2025-01-24 23:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0004_productos'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriasProductos',
            fields=[
                ('IdCategoriaProducto', models.AutoField(primary_key=True, serialize=False)),
                ('IdCategoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias_productos', to='Blyss.categorias')),
                ('IdProducto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias_productos', to='Blyss.productos')),
            ],
        ),
        migrations.CreateModel(
            name='SubcategoriasProductos',
            fields=[
                ('IdSubcategoriaProducto', models.AutoField(primary_key=True, serialize=False)),
                ('IdProducto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias_productos', to='Blyss.productos')),
                ('IdSubcategoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias_productos', to='Blyss.subcategorias')),
            ],
        ),
    ]
