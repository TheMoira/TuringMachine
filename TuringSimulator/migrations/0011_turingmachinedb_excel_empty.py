# Generated by Django 3.1.2 on 2020-12-19 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TuringSimulator', '0010_auto_20201219_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='turingmachinedb',
            name='excel_empty',
            field=models.BooleanField(default=True),
        ),
    ]