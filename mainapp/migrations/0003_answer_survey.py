# Generated by Django 2.2.10 on 2021-10-03 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20211003_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='survey',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='mainapp.Survey'),
            preserve_default=False,
        ),
    ]