# Generated by Django 2.2.7 on 2019-11-18 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('waldur_rancher', '0004_node_backend_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='node',
            unique_together={('cluster', 'name'), ('content_type', 'object_id')},
        ),
    ]
