# Generated by Django 4.2.5 on 2023-10-08 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.RenameField(
            model_name='fooditem',
            old_name='Category',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='fooditem',
            old_name='updated_t',
            new_name='updated_at',
        ),
    ]
