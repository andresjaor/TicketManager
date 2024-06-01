# Generated by Django 5.0.6 on 2024-05-31 13:42

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketimages',
            name='status',
            field=models.CharField(choices=[('UPLOADING', 'Uploading'), ('DONE', 'Done')], default='UPLOADING'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='external_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='num_of_images',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Done')], default='CREATED'),
        ),
    ]