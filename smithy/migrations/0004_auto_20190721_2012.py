# Generated by Django 2.1.5 on 2019-07-22 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smithy', '0003_auto_20190721_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bodyparameter',
            name='value',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='cookie',
            name='value',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='header',
            name='value',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='queryparameter',
            name='value',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='value',
            field=models.TextField(blank=True),
        ),
    ]
