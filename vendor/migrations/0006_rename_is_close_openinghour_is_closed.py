# Generated by Django 4.2.5 on 2023-10-19 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0005_openinghour'),
    ]

    operations = [
        migrations.RenameField(
            model_name='openinghour',
            old_name='is_close',
            new_name='is_closed',
        ),
    ]
