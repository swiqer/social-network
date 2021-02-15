# Generated by Django 2.2.6 on 2020-12-01 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0004_auto_20201126_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True,
                                    help_text='Необязательное поле',
                                    null=True, upload_to='posts/',
                                    verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True,
                help_text='Необязательное поле',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
    ]
