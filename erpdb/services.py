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
        journal_entry.is_posted = True  # Auto-post the entry
        journal_entry.save()
        
        return journal_entry
    
    @staticmethod
    def calculate_account_balance(account, as_of_date):
        """Calculate the balance of an account as of a specific date"""
        # Get all journal lines for this account up to the specified date
        journal_lines = JournalLine.objects.filter(
            account=account,
            journal__date__lte=as_of_date,
            journal__is_posted=True
        )
        
        # Calculate total debits and credits
        total_debits = journal_lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
        total_credits = journal_lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
        
        # Calculate balance based on account type
        if account.account_type in ['asset', 'expense']:
            # Assets and expenses have debit balances
            balance = total_debits - total_credits
        else:
            # Liabilities, equity, and revenue have credit balances
            balance = total_credits - total_debits
        
        return balance

    @staticmethod
    def generate_balance_sheet(as_of_date):
        """Generate balance sheet as of a specific date with real data"""
        accounts = ChartOfAccounts.objects.filter(is_active=True)
        
        balance_sheet = {
            'assets': {
                'current_assets': [],
                'fixed_assets': [],
                'total_current_assets': Decimal('0'),
                'total_fixed_assets': Decimal('0'),
                'total_assets': Decimal('0')
            },
            'liabilities': {
                'current_liabilities': [],
                'long_term_liabilities': [],
                'total_current_liabilities': Decimal('0'),
                'total_long_term_liabilities': Decimal('0'),
                'total_liabilities': Decimal('0')
            },
            'equity': {
                'accounts': [],
                'total_equity': Decimal('0')
            },
            'as_of_date': as_of_date
        }
        
        # Process each account
        for account in accounts:
            balance = AccountingService.calculate_account_balance(account, as_of_date)
            
            if balance == 0:  # Skip accounts with zero balance
                continue
                
            account_data = {
                'account_code': account.account_code,
                'account_name': account.account_name,
                'balance': balance,
                'description': account.description
            }
            
            # Categorize accounts based on their codes and types
            if account.account_type == 'asset':
                if account.account_code.startswith(('100', '110', '120', '130', '140')):
                    # Current assets (typically 100-199 range)
                    balance_sheet['assets']['current_assets'].append(account_data)
                    balance_sheet['assets']['total_current_assets'] += balance
                else:
                    # Fixed assets (typically 150+ range)
                    balance_sheet['assets']['fixed_assets'].append(account_data)
                    balance_sheet['assets']['total_fixed_assets'] += balance
                    
            elif account.account_type == 'liability':
                if account.account_code.startswith(('200', '210', '220')):
                    # Current liabilities (typically 200-299 range)
                    balance_sheet['liabilities']['current_liabilities'].append(account_data)
                    balance_sheet['liabilities']['total_current_liabilities'] += balance
                else:
                    # Long-term liabilities (typically 250+ range)
                    balance_sheet['liabilities']['long_term_liabilities'].append(account_data)
                    balance_sheet['liabilities']['total_long_term_liabilities'] += balance
                    
            elif account.account_type == 'equity':
                balance_sheet['equity']['accounts'].append(account_data)
                balance_sheet['equity']['total_equity'] += balance
        
        # Calculate totals
        balance_sheet['assets']['total_assets'] = (
            balance_sheet['assets']['total_current_assets'] + 
            balance_sheet['assets']['total_fixed_assets']
        )
        
        balance_sheet['liabilities']['total_liabilities'] = (
            balance_sheet['liabilities']['total_current_liabilities'] + 
            balance_sheet['liabilities']['total_long_term_liabilities']
        )
        
        # Calculate retained earnings from P&L if not explicitly tracked
        if not any(acc['account_name'].lower().find('retained') != -1 for acc in balance_sheet['equity']['accounts']):
            # Calculate retained earnings from sales and expenses
            retained_earnings = AccountingService.calculate_retained_earnings(as_of_date)
            if retained_earnings != 0:
                balance_sheet['equity']['accounts'].append({
                    'account_code': '350',
                    'account_name': 'Retained Earnings',
                    'balance': retained_earnings,
                    'description': 'Accumulated profits/losses'
                })
                balance_sheet['equity']['total_equity'] += retained_earnings
        
        return balance_sheet

    @staticmethod
    def calculate_retained_earnings(as_of_date):
        """Calculate retained earnings from sales and expenses"""
        # Get all revenue accounts
        revenue_accounts = ChartOfAccounts.objects.filter(
            account_type='revenue',
            is_active=True
        )
        
        # Get all expense accounts
        expense_accounts = ChartOfAccounts.objects.filter(
            account_type='expense',
            is_active=True
        )
        
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')
        
        # Calculate total revenue
        for account in revenue_accounts:
            balance = AccountingService.calculate_account_balance(account, as_of_date)
            total_revenue += balance
        
        # Calculate total expenses
        for account in expense_accounts:
            balance = AccountingService.calculate_account_balance(account, as_of_date)
            total_expenses += balance
        
        # Retained earnings = Revenue - Expenses
        return total_revenue - total_expenses

    @staticmethod
    def create_default_chart_of_accounts():
        """Create default chart of accounts if none exist"""
        if ChartOfAccounts.objects.exists():
            return  # Already exists
        
        default_accounts = [
            # Assets
            {'code': '100', 'name': 'Cash', 'type': 'asset', 'description': 'Cash on hand and in bank'},
            {'code': '110', 'name': 'Accounts Receivable', 'type': 'asset', 'description': 'Amounts owed by customers'},
            {'code': '120', 'name': 'Inventory', 'type': 'asset', 'description': 'Stock on hand'},
            {'code': '130', 'name': 'Prepaid Expenses', 'type': 'asset', 'description': 'Prepaid insurance, rent, etc.'},
            {'code': '150', 'name': 'Equipment', 'type': 'asset', 'description': 'Office equipment and machinery'},
            {'code': '160', 'name': 'Accumulated Depreciation', 'type': 'asset', 'description': 'Depreciation on equipment'},
            
            # Liabilities
            {'code': '200', 'name': 'Accounts Payable', 'type': 'liability', 'description': 'Amounts owed to suppliers'},
            {'code': '210', 'name': 'Accrued Expenses', 'type': 'liability', 'description': 'Accrued wages, utilities, etc.'},
            {'code': '220', 'name': 'Short-term Debt', 'type': 'liability', 'description': 'Short-term loans and credit'},
            {'code': '250', 'name': 'Long-term Debt', 'type': 'liability', 'description': 'Long-term loans and mortgages'},
            
            # Equity
            {'code': '300', 'name': 'Owner\'s Equity', 'type': 'equity', 'description': 'Initial capital investment'},
            {'code': '350', 'name': 'Retained Earnings', 'type': 'equity', 'description': 'Accumulated profits/losses'},
            
            # Revenue
            {'code': '400', 'name': 'Sales Revenue', 'type': 'revenue', 'description': 'Revenue from sales'},
            {'code': '410', 'name': 'Service Revenue', 'type': 'revenue', 'description': 'Revenue from services'},
            
            # Expenses
            {'code': '500', 'name': 'Cost of Goods Sold', 'type': 'expense', 'description': 'Direct costs of products sold'},
            {'code': '510', 'name': 'Salaries and Wages', 'type': 'expense', 'description': 'Employee compensation'},
            {'code': '520', 'name': 'Rent Expense', 'type': 'expense', 'description': 'Office and warehouse rent'},
            {'code': '530', 'name': 'Utilities Expense', 'type': 'expense', 'description': 'Electricity, water, internet'},
            {'code': '540', 'name': 'Office Supplies', 'type': 'expense', 'description': 'Office supplies and materials'},
            {'code': '550', 'name': 'Depreciation Expense', 'type': 'expense', 'description': 'Depreciation on equipment'},
        ]
        
        for account_data in default_accounts:
            ChartOfAccounts.objects.create(
                account_code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                description=account_data['description']
            )

    @staticmethod
    def create_sample_journal_entries(user):
        """Create sample journal entries for demonstration purposes"""
        from datetime import date, timedelta
        
        # Get some accounts
        cash_account = ChartOfAccounts.objects.get(account_code='100')
        ar_account = ChartOfAccounts.objects.get(account_code='110')
        inventory_account = ChartOfAccounts.objects.get(account_code='120')
        equipment_account = ChartOfAccounts.objects.get(account_code='150')
        ap_account = ChartOfAccounts.objects.get(account_code='200')
        equity_account = ChartOfAccounts.objects.get(account_code='300')
        sales_account = ChartOfAccounts.objects.get(account_code='400')
        cogs_account = ChartOfAccounts.objects.get(account_code='500')
        
        # Sample journal entries
        sample_entries = [
            {
                'date': date.today() - timedelta(days=30),
                'description': 'Initial capital investment',
                'entry_type': 'manual',
                'lines': [
                    {'account': cash_account, 'debit': Decimal('100000'), 'credit': Decimal('0'), 'description': 'Initial cash investment'},
                    {'account': equity_account, 'debit': Decimal('0'), 'credit': Decimal('100000'), 'description': 'Owner equity'},
                ]
            },
            {
                'date': date.today() - timedelta(days=25),
                'description': 'Purchase of equipment',
                'entry_type': 'purchase',
                'lines': [
                    {'account': equipment_account, 'debit': Decimal('25000'), 'credit': Decimal('0'), 'description': 'Office equipment'},
                    {'account': cash_account, 'debit': Decimal('0'), 'credit': Decimal('25000'), 'description': 'Cash payment'},
                ]
            },
            {
                'date': date.today() - timedelta(days=20),
                'description': 'Purchase inventory on credit',
                'entry_type': 'purchase',
                'lines': [
                    {'account': inventory_account, 'debit': Decimal('15000'), 'credit': Decimal('0'), 'description': 'Inventory purchase'},
                    {'account': ap_account, 'debit': Decimal('0'), 'credit': Decimal('15000'), 'description': 'Accounts payable'},
                ]
            },
            {
                'date': date.today() - timedelta(days=15),
                'description': 'Sales on credit',
                'entry_type': 'sales',
                'lines': [
                    {'account': ar_account, 'debit': Decimal('8000'), 'credit': Decimal('0'), 'description': 'Accounts receivable'},
                    {'account': sales_account, 'debit': Decimal('0'), 'credit': Decimal('8000'), 'description': 'Sales revenue'},
                ]
            },
            {
                'date': date.today() - timedelta(days=10),
                'description': 'Cost of goods sold',
                'entry_type': 'sales',
                'lines': [
                    {'account': cogs_account, 'debit': Decimal('5000'), 'credit': Decimal('0'), 'description': 'Cost of goods sold'},
                    {'account': inventory_account, 'debit': Decimal('0'), 'credit': Decimal('5000'), 'description': 'Inventory reduction'},
                ]
            },
            {
                'date': date.today() - timedelta(days=5),
                'description': 'Payment to supplier',
                'entry_type': 'payment',
                'lines': [
                    {'account': ap_account, 'debit': Decimal('10000'), 'credit': Decimal('0'), 'description': 'Payment to supplier'},
                    {'account': cash_account, 'debit': Decimal('0'), 'credit': Decimal('10000'), 'description': 'Cash payment'},
                ]
            }
        ]
        
        # Create the journal entries
        for entry_data in sample_entries:
            try:
                AccountingService.create_journal_entry(
                    date=entry_data['date'],
                    description=entry_data['description'],
                    entry_type=entry_data['entry_type'],
                    lines_data=entry_data['lines'],
                    user=user
                )
            except Exception as e:
                print(f"Error creating journal entry: {e}")
                continue

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
