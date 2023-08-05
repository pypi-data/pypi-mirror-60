# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-09-09 13:00
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
import waldur_core.core.shims
import waldur_core.core.fields
import waldur_core.core.models
import waldur_core.core.validators
import waldur_core.logging.loggers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('structure', '0001_squashed_0054'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('taggit', '0002_auto_20150616_2121'),
        ('quotas', '0001_squashed_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(db_index=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Root disk size in MiB')),
                ('settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='structure.ServiceSettings')),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FloatingIP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('address', models.GenericIPAddressField(protocol='IPv4')),
                ('status', models.CharField(max_length=30)),
                ('backend_id', models.CharField(max_length=255)),
                ('backend_network_id', models.CharField(editable=False, max_length=255)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Floating IP',
                'verbose_name_plural': 'Floating IPs',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(db_index=True, max_length=255)),
                ('min_disk', models.PositiveIntegerField(default=0, help_text='Minimum disk size in MiB')),
                ('min_ram', models.PositiveIntegerField(default=0, help_text='Minimum memory size in MiB')),
                ('settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='structure.ServiceSettings')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OpenStackService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Customer', verbose_name='organization')),
            ],
            options={
                'verbose_name': 'OpenStack provider',
                'verbose_name_plural': 'OpenStack providers',
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OpenStackServiceProjectLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Project')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openstack.OpenStackService')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'OpenStack provider project link',
                'verbose_name_plural': 'OpenStack provider project links',
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SecurityGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=128)),
                ('service_project_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='security_groups', to='openstack.OpenStackServiceProjectLink')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SecurityGroupRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(blank=True, choices=[('tcp', 'tcp'), ('udp', 'udp'), ('icmp', 'icmp')], max_length=4)),
                ('from_port', models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('to_port', models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('cidr', models.CharField(blank=True, max_length=32)),
                ('backend_id', models.CharField(blank=True, max_length=128)),
                ('security_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='openstack.SecurityGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('runtime_state', models.CharField(blank=True, max_length=150, verbose_name='runtime state')),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=255)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('internal_network_id', models.CharField(blank=True, max_length=64)),
                ('external_network_id', models.CharField(blank=True, max_length=64)),
                ('availability_zone', models.CharField(blank=True, help_text='Optional availability group. Will be used for all instances provisioned in this tenant', max_length=100)),
                ('user_username', models.CharField(blank=True, max_length=50)),
                ('user_password', models.CharField(blank=True, max_length=50)),
                ('service_project_link', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tenants', to='openstack.OpenStackServiceProjectLink')),
                ('tags', waldur_core.core.shims.TaggableManager(related_name='+', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('extra_configuration', waldur_core.core.fields.JSONField(default={}, help_text='Configuration details that are not represented on backend.')),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.AddField(
            model_name='openstackservice',
            name='projects',
            field=models.ManyToManyField('structure.Project', related_name='openstack_services', through='openstack.OpenStackServiceProjectLink'),
        ),
        migrations.AddField(
            model_name='openstackservice',
            name='settings',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.ServiceSettings'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='service_project_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floating_ips', to='openstack.OpenStackServiceProjectLink'),
        ),
        migrations.AlterUniqueTogether(
            name='openstackserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
        migrations.RemoveField(
            model_name='openstackservice',
            name='name',
        ),
        migrations.AlterUniqueTogether(
            name='openstackservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('settings', 'backend_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='flavor',
            unique_together=set([('settings', 'backend_id')]),
        ),
        migrations.AddField(
            model_name='securitygroup',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='security_groups', to='openstack.Tenant'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floating_ips', to='openstack.Tenant'),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('runtime_state', models.CharField(blank=True, max_length=150, verbose_name='runtime state')),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=255)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('is_external', models.BooleanField(default=False)),
                ('type', models.CharField(blank=True, max_length=50)),
                ('segmentation_id', models.IntegerField(null=True)),
                ('service_project_link', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='networks', to='openstack.OpenStackServiceProjectLink')),
                ('tags', waldur_core.core.shims.TaggableManager(related_name='+', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='networks', to='openstack.Tenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubNet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=255)),
                ('cidr', models.CharField(blank=True, max_length=32)),
                ('gateway_ip', models.GenericIPAddressField(null=True, protocol='IPv4')),
                ('allocation_pools', waldur_core.core.fields.JSONField(default=dict)),
                ('ip_version', models.SmallIntegerField(default=4)),
                ('enable_dhcp', models.BooleanField(default=True)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subnets', to='openstack.Network')),
                ('service_project_link', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subnets', to='openstack.OpenStackServiceProjectLink')),
                ('tags', waldur_core.core.shims.TaggableManager(related_name='+', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('dns_nameservers', waldur_core.core.fields.JSONField(default=list, help_text='List of DNS name servers associated with the subnet.')),
                ('disable_gateway', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Subnet',
                'verbose_name_plural': 'Subnets',
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='description',
            field=models.CharField(blank=True, max_length=500, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='error_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='name',
            field=models.CharField(default='', max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='floatingip',
            name='runtime_state',
            field=models.CharField(blank=True, max_length=150, verbose_name='runtime state'),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='state',
            field=django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5),
        ),
        migrations.AddField(
            model_name='floatingip',
            name='tags',
            field=waldur_core.core.shims.TaggableManager(related_name='+', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='floatingip',
            name='address',
            field=models.GenericIPAddressField(blank=True, null=True, protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='floatingip',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RemoveField(
            model_name='floatingip',
            name='status',
        ),
        migrations.AddField(
            model_name='securitygroup',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='securitygroup',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='securitygroup',
            name='tags',
            field=waldur_core.core.shims.TaggableManager(related_name='+', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='securitygroup',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RemoveField(
            model_name='network',
            name='start_time',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='start_time',
        ),
        migrations.CreateModel(
            name='CustomerOpenStack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('external_network_id', models.CharField(max_length=255, verbose_name='OpenStack external network ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Customer')),
                ('settings', models.ForeignKey(limit_choices_to={'shared': True, 'type': 'OpenStack'}, on_delete=django.db.models.deletion.CASCADE, to='structure.ServiceSettings')),
            ],
            options={
                'verbose_name': 'Organization OpenStack settings',
                'verbose_name_plural': 'Organization OpenStack settings',
            },
        ),
        migrations.AlterUniqueTogether(
            name='customeropenstack',
            unique_together=set([('settings', 'customer')]),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='extra_configuration',
            field=waldur_core.core.fields.JSONField(default=dict, help_text='Configuration details that are not represented on backend.'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='default_volume_type_name',
            field=models.CharField(blank=True, help_text='Volume type name to use when creating volumes.', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='tenant',
            unique_together=set([('service_project_link', 'backend_id')]),
        ),
        migrations.AlterField(
            model_name='floatingip',
            name='address',
            field=models.GenericIPAddressField(blank=True, default=None, null=True, protocol='IPv4'),
        ),
        migrations.AlterUniqueTogether(
            name='floatingip',
            unique_together=set([('tenant', 'address')]),
        ),
    ]
