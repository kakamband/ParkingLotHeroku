# Generated by Django 3.1.4 on 2020-12-08 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0007_auto_20201208_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='level',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='car',
            name='slot',
            field=models.IntegerField(default=100),
        ),
    ]
