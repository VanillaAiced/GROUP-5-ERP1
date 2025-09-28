from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('erpdb', '0002_alter_category_options_alter_warehouse_options_and_more'),
    ]

    operations = [
        # Rename fields
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='expected_delivery',
            new_name='delivery_date',
        ),
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='order_number',
            new_name='po_number',
        ),

        # Remove fields
        migrations.RemoveField(
            model_name='purchaseorder',
            name='paid_amount',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='tax_rate',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='line_total',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='unit_cost',
        ),

        # Add fields to PurchaseOrder with defaults
        migrations.AddField(
            model_name='purchaseorder',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='payment_terms',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='reference_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='warehouse',
            field=models.ForeignKey(default=1, on_delete=models.deletion.CASCADE, to='erpdb.warehouse'),
            preserve_default=False,
        ),

        # Add fields to PurchaseOrderItem with defaults
        migrations.AddField(
            model_name='purchaseorderitem',
            name='received_quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0.01, max_digits=12),
            preserve_default=False,
        ),

        # Alter field status on purchase order to match the model's choices
        migrations.AlterField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('confirmed', 'Confirmed'), ('received', 'Received'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='draft', max_length=20),
        ),
    ]
