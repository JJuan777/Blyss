# Generated by Django 5.0.9 on 2025-02-11 18:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blyss', '0017_bannerhome_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direcciones',
            fields=[
                ('IdDirecciones', models.AutoField(primary_key=True, serialize=False)),
                ('Estado', models.CharField(max_length=100)),
                ('CP', models.CharField(max_length=10)),
                ('Municipio', models.CharField(max_length=100)),
                ('Ciudad', models.CharField(max_length=100)),
                ('Colonia', models.CharField(max_length=150)),
                ('Calle', models.CharField(max_length=150)),
                ('Numero_Exterior', models.CharField(max_length=10)),
                ('Numero_Interior', models.CharField(blank=True, max_length=10, null=True)),
                ('Referencias', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DireccionesUsuario',
            fields=[
                ('IdDireccionUsuario', models.AutoField(primary_key=True, serialize=False)),
                ('IdDirecciones', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuarios_direccion', to='Blyss.direcciones')),
                ('IdUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='direcciones_usuario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dirección de Usuario',
                'verbose_name_plural': 'Direcciones de Usuarios',
                'unique_together': {('IdDirecciones', 'IdUsuario')},
            },
        ),
    ]
