# Generated manually to add invoice field to Payment model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erpdb', '0005_alter_invoice_options_invoice_discount_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='erpdb.invoice'),
        ),
    ]

