# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-04 21:55
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0007_0_3_3'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='auto_renew',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='option',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='plan',
            name='renewal_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'ONE_TIME'), (1, 'AUTO_RENEW'), (2, 'REPEAT')], default=1),
        ),
        migrations.AddField(
            model_name='usecharge',
            name='quota',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='balanceline',
            name='rank',
            field=models.IntegerField(help_text='Absolute position of the row in the list of rows for the table'),
        ),
        migrations.AlterField(
            model_name='balanceline',
            name='selector',
            field=models.CharField(blank=True, help_text='Filter on the Transaction accounts', max_length=255),
        ),
        migrations.AlterField(
            model_name='balanceline',
            name='title',
            field=models.CharField(help_text='Title for the row', max_length=255),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='coupon',
            field=models.ForeignKey(blank=True, help_text='Coupon to apply to the order', null=True, on_delete=django.db.models.deletion.CASCADE, to='saas.Coupon'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='first_name',
            field=models.CharField(blank=True, help_text='First name of the person that will benefit from the subscription (GroupBuy)', max_length=30, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='last_name',
            field=models.CharField(blank=True, help_text='Last name of the person that will benefit from the subscription (GroupBuy)', max_length=30, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='plan',
            field=models.ForeignKey(help_text='Item added to the cart (if plan)', null=True, on_delete=django.db.models.deletion.CASCADE, to='saas.Plan'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=0, help_text='Number of periods to be paid in advance'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='recorded',
            field=models.BooleanField(default=False, help_text='Whever the item has been checked out or not'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='use',
            field=models.ForeignKey(help_text='Item added to the cart (if use charge)', null=True, on_delete=django.db.models.deletion.CASCADE, to='saas.UseCharge'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='user',
            field=models.ForeignKey(db_column='user_id', help_text='User who added the item to the cart (``None`` means the item could be claimed)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='charge',
            name='amount',
            field=models.PositiveIntegerField(default=0, help_text='Total amount in currency unit'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='created_at',
            field=models.DateTimeField(help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(help_text='Organization charged', on_delete=django.db.models.deletion.PROTECT, to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='description',
            field=models.TextField(help_text='Description for the Charge as appears on billing statements', null=True),
        ),
        migrations.AlterField(
            model_name='charge',
            name='exp_date',
            field=models.DateField(help_text='Expiration date of the credit card used'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='charge',
            name='last4',
            field=models.PositiveSmallIntegerField(help_text='Last 4 digits of the credit card used'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(1, 'done'), (0, 'created'), (2, 'failed'), (3, 'disputed')], default=0, help_text='Current state (i.e. created, done, failed, disputed)'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='unit',
            field=models.CharField(default='usd', help_text='Three-letter ISO 4217 code for currency unit (ex: usd)', max_length=3),
        ),
        migrations.AlterField(
            model_name='chargeitem',
            name='invoiced',
            field=models.ForeignKey(help_text='Transaction invoiced through this charge', on_delete=django.db.models.deletion.PROTECT, related_name='invoiced_item', to='saas.Transaction'),
        ),
        migrations.AlterField(
            model_name='chargeitem',
            name='invoiced_distribute',
            field=models.ForeignKey(help_text='Transaction recording the distribution from processor to provider.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoiced_distribute', to='saas.Transaction'),
        ),
        migrations.AlterField(
            model_name='chargeitem',
            name='invoiced_fee',
            field=models.ForeignKey(help_text='Fee transaction to process the transaction invoiced through this charge', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoiced_fee_item', to='saas.Transaction'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.SlugField(help_text='Unique identifier per provider, typically used in URLs'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='description',
            field=models.TextField(blank=True, help_text='Free-form text description for the Coupon', null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='ends_at',
            field=models.DateTimeField(blank=True, help_text='Date/time at which the coupon code expires (in ISO format)', null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='organization',
            field=models.ForeignKey(help_text='Coupon will only apply to purchased plans from this provider', on_delete=django.db.models.deletion.CASCADE, to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='plan',
            field=models.ForeignKey(blank=True, help_text='Coupon will only apply to this plan', null=True, on_delete=django.db.models.deletion.CASCADE, to='saas.Plan'),
        ),
        migrations.AlterField(
            model_name='role',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role', to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='role',
            name='user',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='role', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='roledescription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='roledescription',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='roledescription',
            name='slug',
            field=models.SlugField(help_text='Unique identifier shown in the URL bar'),
        ),
        migrations.AlterField(
            model_name='roledescription',
            name='title',
            field=models.CharField(help_text='Short description of the role. Grammatical rules to pluralize the title might be used in User Interfaces.', max_length=20),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='auto_renew',
            field=models.BooleanField(default=True, help_text='The subscription is set to auto-renew at the end of the period'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='description',
            field=models.TextField(blank=True, help_text='Free-form text description for the subscription', null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='ends_at',
            field=models.DateTimeField(help_text='Date/time when the subscription period currently ends (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='organization',
            field=models.ForeignKey(help_text='Organization subscribed to the plan', on_delete=django.db.models.deletion.CASCADE, to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(help_text='Plan the organization is subscribed to', on_delete=django.db.models.deletion.CASCADE, to='saas.Plan'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(help_text='Date/time of creation (in ISO format)'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='descr',
            field=models.TextField(default='N/A', help_text='Free-form text description for the Transaction'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='dest_account',
            field=models.CharField(default='unknown', help_text='Target account to which funds are deposited', max_length=255),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='dest_amount',
            field=models.PositiveIntegerField(default=0, help_text='Amount deposited into target in dest_unit'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='dest_organization',
            field=models.ForeignKey(help_text='Target organization to which funds are deposited', on_delete=django.db.models.deletion.PROTECT, related_name='incoming', to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='dest_unit',
            field=models.CharField(default='usd', help_text='Three-letter ISO 4217 code for target currency unit (ex: usd)', max_length=3),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='event_id',
            field=models.SlugField(help_text='Event at the origin of this transaction (ex. subscription, charge, etc.)', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='orig_account',
            field=models.CharField(default='unknown', help_text='Source account from which funds are withdrawn', max_length=255),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='orig_amount',
            field=models.PositiveIntegerField(default=0, help_text='Amount withdrawn from source in orig_unit'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='orig_organization',
            field=models.ForeignKey(help_text='Source organization from which funds are withdrawn', on_delete=django.db.models.deletion.PROTECT, related_name='outgoing', to='saas.Organization'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='orig_unit',
            field=models.CharField(default='usd', help_text='Three-letter ISO 4217 code for source currency unit (ex: usd)', max_length=3),
        ),
        migrations.AlterField(
            model_name='usecharge',
            name='extra',
            field=models.TextField(help_text='Extra meta data (can be stringify JSON)', null=True),
        ),
        migrations.AlterField(
            model_name='usecharge',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='use_charges', to='saas.Plan'),
        ),
    ]
