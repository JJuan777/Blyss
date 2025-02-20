# Generated by Django 5.0.9 on 2025-01-31 22:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0010_remove_categoriasproductos_imagen_categorias_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerCategorias',
            fields=[
                ('IdBannerCat', models.AutoField(primary_key=True, serialize=False)),
                ('ImagenBanner', models.BinaryField(blank=True, null=True)),
                ('Estado', models.BooleanField(default=True)),
                ('Orden', models.PositiveIntegerField(default=1)),
                ('FechaCreacion', models.DateTimeField(auto_now_add=True)),
                ('IdCategoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='Blyss.categorias')),
            ],
            options={
                'ordering': ['Orden'],
            },
        ),
    ]
