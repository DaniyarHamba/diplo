# Generated by Django 5.0.6 on 2024-06-20 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_videocomment_video'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VideoComment',
        ),
    ]
