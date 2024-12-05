# Generated by Django 3.1.14 on 2022-03-09 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0088_auto_20220303_1612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='authbook',
            options={'permissions': [('test_authbook', 'Can test asset account connectivity'), ('view_assetaccountsecret', 'Can view asset account secret'), ('change_assetaccountsecret', 'Can change asset account secret')], 'verbose_name': 'AuthBook'},
        ),
        migrations.AlterModelOptions(
            name='systemuser',
            options={'ordering': ['name'], 'permissions': [('match_systemuser', 'Can match system user')], 'verbose_name': 'System user'},
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['hostname'], 'permissions': [('refresh_assethardwareinfo', 'Can refresh asset hardware info'), ('test_assetconnectivity', 'Can test asset connectivity'), ('push_assetsystemuser', 'Can push system user to asset'), ('match_asset', 'Can match asset'), ('add_assettonode', 'Add asset to node'), ('move_assettonode', 'Move asset to node')], 'verbose_name': 'Asset'},
        ),
        migrations.AlterModelOptions(
            name='gateway',
            options={'permissions': [('test_gateway', 'Test gateway')], 'verbose_name': 'Gateway'},
        ),
    ]
