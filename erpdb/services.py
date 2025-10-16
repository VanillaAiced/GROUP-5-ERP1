from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import (
    Customer, Vendor, Category, Product, Warehouse, Inventory,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    ChartOfAccounts, JournalEntry, JournalLine,
    Department, Position, Employee, InventoryTransaction, FinancialReport
)

class DashboardService:
    @staticmethod
    def get_dashboard_data():
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        
        return {
            "customer_count": Customer.objects.filter(is_active=True).count(),
            "vendor_count": Vendor.objects.filter(is_active=True).count(),
            "product_count": Product.objects.filter(is_active=True).count(),
            "sales_order_count": SalesOrder.objects.count(),
            "purchase_order_count": PurchaseOrder.objects.count(),
            "employee_count": Employee.objects.filter(employment_status='active').count(),
            "total_sales_this_month": SalesOrder.objects.filter(
                order_date__date__gte=this_month_start,
                status__in=['completed', 'delivered']
            ).aggregate(total=models.Sum('total_amount'))['total'] or 0,
            "pending_orders": SalesOrder.objects.filter(status='pending').count(),
            "low_stock_products": Inventory.objects.filter(
                quantity_available__lte=models.F('reorder_point')
            ).count(),
        }

class InventoryService:
    @staticmethod
    @transaction.atomic
    def create_inventory_transaction(transaction_type, product, warehouse, quantity, user, reference_number=None, notes=None):
        """Create an inventory transaction and update inventory levels"""
        # Create the transaction
        transaction_obj = InventoryTransaction.objects.create(
            transaction_type=transaction_type,
            product=product,
            warehouse=warehouse,
            quantity=quantity,
            reference_number=reference_number,
            notes=notes,
            created_by=user
        )
        
        # Update inventory levels
        inventory, created = Inventory.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={
                'quantity_on_hand': 0,
                'quantity_reserved': 0,
                'quantity_available': 0
            }
        )
        
        if transaction_type in ['in', 'return']:
            inventory.quantity_on_hand += quantity
        elif transaction_type in ['out', 'transfer']:
            inventory.quantity_on_hand -= quantity
        elif transaction_type == 'adjustment':
            inventory.quantity_on_hand = quantity
        
        inventory.save()
        
        return transaction_obj
    
    @staticmethod
    def get_low_stock_items():
        """Get items that are below reorder point"""
        return Inventory.objects.filter(
            quantity_available__lte=models.F('reorder_point')
        ).select_related('product', 'warehouse')
    
    @staticmethod
    def check_stock_availability(product, warehouse, quantity):
        """Check if sufficient stock is available"""
        try:
            inventory = Inventory.objects.get(product=product, warehouse=warehouse)
            return inventory.quantity_available >= quantity
        except Inventory.DoesNotExist:
            return False

class SalesService:
    @staticmethod
    @transaction.atomic
    def create_sales_order(customer, items_data, user, delivery_date=None, notes=None):
        """Create a sales order with items"""
        # Generate order number
        order_number = f"SO-{timezone.now().strftime('%Y%m%d')}-{SalesOrder.objects.count() + 1:04d}"
        
        # Create sales order
        sales_order = SalesOrder.objects.create(
            order_number=order_number,
            customer=customer,
            delivery_date=delivery_date,
            notes=notes,
            created_by=user
        )
        
        subtotal = Decimal('0')
        
        # Create order items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = item_data.get('unit_price', product.unit_price)
            discount_percent = item_data.get('discount_percent', 0)
            
            # Check stock availability
            if not InventoryService.check_stock_availability(product, item_data.get('warehouse'), quantity):
                raise ValueError(f"Insufficient stock for {product.name}")
            
            # Create order item
            order_item = SalesOrderItem.objects.create(
                order=sales_order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                discount_percent=discount_percent
            )
            
            subtotal += order_item.line_total
        
        # Update order totals
        sales_order.subtotal = subtotal
        sales_order.tax_amount = subtotal * Decimal('0.1')  # 10% tax
        sales_order.total_amount = subtotal + sales_order.tax_amount
        sales_order.save()
        
        return sales_order
    
    @staticmethod
    @transaction.atomic
    def process_sales_order(order_id):
        """Process a sales order and update inventory"""
        order = SalesOrder.objects.get(id=order_id)
        
        if order.status != 'pending':
            raise ValueError("Order is not in pending status")
        
        # Update inventory for each item
        for item in order.items.all():
            InventoryService.create_inventory_transaction(
                transaction_type='out',
                product=item.product,
                warehouse=item.product.warehouse_set.first(),  # Default warehouse
                quantity=item.quantity,
                user=order.created_by,
                reference_number=order.order_number,
                notes=f"Sales order {order.order_number}"
            )
        
        # Update order status
        order.status = 'confirmed'
        order.save()
        
        return order

class AccountingService:
    @staticmethod
    @transaction.atomic
    def create_journal_entry(date, description, entry_type, lines_data, user):
        """Create a journal entry with lines"""
        # Generate entry number
        entry_number = f"JE-{timezone.now().strftime('%Y%m%d')}-{JournalEntry.objects.count() + 1:04d}"
        
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            entry_number=entry_number,
            date=date,
            description=description,
            entry_type=entry_type,
            created_by=user
        )
        
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        # Create journal lines
        for line_data in lines_data:
            account = line_data['account']
            debit = line_data.get('debit', 0)
            credit = line_data.get('credit', 0)
            description = line_data.get('description', '')
            
            JournalLine.objects.create(
                journal=journal_entry,
                account=account,
                description=description,
                debit=debit,
                credit=credit
            )
            
            total_debit += debit
            total_credit += credit
        
        # Validate double-entry bookkeeping
        if total_debit != total_credit:
            raise ValueError("Total debits must equal total credits")
        
        # Update journal entry totals
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
        journal_entry.save()
        
        return journal_entry
    
    @staticmethod
    def generate_balance_sheet(as_of_date):
        """Generate balance sheet as of a specific date"""
        # This is a simplified version - in production, you'd have more complex logic
        accounts = ChartOfAccounts.objects.filter(is_active=True)
        
        balance_sheet = {
            'assets': [],
            'liabilities': [],
            'equity': []
        }
        
        for account in accounts:
            # Calculate account balance (simplified)
            balance = Decimal('0')  # This would be calculated from journal entries
            
            account_data = {
                'account_code': account.account_code,
                'account_name': account.account_name,
                'balance': balance
            }
            
            if account.account_type == 'asset':
                balance_sheet['assets'].append(account_data)
            elif account.account_type == 'liability':
                balance_sheet['liabilities'].append(account_data)
            elif account.account_type == 'equity':
                balance_sheet['equity'].append(account_data)
        
        return balance_sheet

class ReportService:
    @staticmethod
    def generate_sales_report(start_date, end_date):
        """Generate sales report for date range"""
        orders = SalesOrder.objects.filter(
            order_date__date__range=[start_date, end_date],
            status__in=['completed', 'delivered']
        )
        
        total_sales = orders.aggregate(total=models.Sum('total_amount'))['total'] or 0
        order_count = orders.count()
        
        # Sales by customer
        sales_by_customer = orders.values('customer__name').annotate(
            total=models.Sum('total_amount'),
            count=models.Count('id')
        ).order_by('-total')
        
        # Sales by product
        sales_by_product = SalesOrderItem.objects.filter(
            order__order_date__date__range=[start_date, end_date],
            order__status__in=['completed', 'delivered']
        ).values('product__name').annotate(
            total=models.Sum('line_total'),
            quantity=models.Sum('quantity')
        ).order_by('-total')
        
        return {
            'total_sales': total_sales,
            'order_count': order_count,
            'sales_by_customer': sales_by_customer,
            'sales_by_product': sales_by_product,
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def generate_inventory_report():
        """Generate inventory report"""
        inventory = Inventory.objects.select_related('product', 'warehouse').all()
        
        total_value = sum(
            item.quantity_on_hand * item.product.cost_price 
            for item in inventory
        )
        
        low_stock_items = InventoryService.get_low_stock_items()
        
        return {
            'total_items': inventory.count(),
            'total_value': total_value,
            'low_stock_count': low_stock_items.count(),
            'low_stock_items': low_stock_items
        }

class NotificationService:
    @staticmethod
    def check_low_stock_alerts():
        """Check for low stock items and create alerts"""
        low_stock_items = InventoryService.get_low_stock_items()
        
        alerts = []
        for item in low_stock_items:
            alerts.append({
                'type': 'low_stock',
                'message': f"{item.product.name} is below reorder point in {item.warehouse.name}",
                'product': item.product,
                'warehouse': item.warehouse,
                'current_stock': item.quantity_available,
                'reorder_point': item.reorder_point
            })
        
        return alerts
