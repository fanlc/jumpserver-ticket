# Generated by Django 3.1 on 2021-01-03 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perms', '0016_applicationpermission'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='k8sapppermission',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='k8sapppermission',
            name='k8s_apps',
        ),
        migrations.RemoveField(
            model_name='k8sapppermission',
            name='system_users',
        ),
        migrations.RemoveField(
            model_name='k8sapppermission',
            name='user_groups',
        ),
        migrations.RemoveField(
            model_name='k8sapppermission',
            name='users',
        ),
        migrations.AlterUniqueTogether(
            name='remoteapppermission',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='remoteapppermission',
            name='remote_apps',
        ),
        migrations.RemoveField(
            model_name='remoteapppermission',
            name='system_users',
        ),
        migrations.RemoveField(
            model_name='remoteapppermission',
            name='user_groups',
        ),
        migrations.RemoveField(
            model_name='remoteapppermission',
            name='users',
        ),
        migrations.DeleteModel(
            name='DatabaseAppPermission',
        ),
        migrations.DeleteModel(
            name='K8sAppPermission',
        ),
        migrations.DeleteModel(
            name='RemoteAppPermission',
        ),
    ]
