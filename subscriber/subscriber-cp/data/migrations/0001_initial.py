# Generated by Django 3.0.5 on 2020-06-08 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KnownHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=100)),
                ('port', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
            options={
                'unique_together': {('host', 'port', 'user', 'password')},
            },
        ),
    ]