# Generated by Django 2.0.6 on 2018-09-18 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='phone_number',
            field=models.CharField(max_length=16, null=True),
        ),
    ]
