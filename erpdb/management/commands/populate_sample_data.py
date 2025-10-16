from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from erpdb.models import (
    Customer, Vendor, Category, Product, Warehouse, Inventory,
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    ChartOfAccounts, JournalEntry, JournalLine,
    Department, Position, Employee, InventoryTransaction,
    Payment, Invoice
)

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to populate sample data...')

        with transaction.atomic():
            # Create a superuser if one doesn't exist
            if not User.objects.filter(is_superuser=True).exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
            else:
                admin_user = User.objects.filter(is_superuser=True).first()
                self.stdout.write('Superuser already exists')

            # Create categories
            categories = self._create_categories()
            self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

            # Create warehouses
            warehouses = self._create_warehouses()
            self.stdout.write(self.style.SUCCESS(f'Created {len(warehouses)} warehouses'))

            # Create products
            products = self._create_products(categories)
            self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

            # Create inventory
            self._create_inventory(products, warehouses)
            self.stdout.write(self.style.SUCCESS('Created inventory records'))

            # Create customers
            customers = self._create_customers(admin_user)
            self.stdout.write(self.style.SUCCESS(f'Created {len(customers)} customers'))

            # Create vendors
            vendors = self._create_vendors(admin_user)
            self.stdout.write(self.style.SUCCESS(f'Created {len(vendors)} vendors'))

            # Create chart of accounts
            accounts = self._create_chart_of_accounts()
            self.stdout.write(self.style.SUCCESS(f'Created {len(accounts)} accounts'))

            # Create departments
            departments = self._create_departments(admin_user)
            self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments'))

            # Create positions
            positions = self._create_positions(departments)
            self.stdout.write(self.style.SUCCESS(f'Created {len(positions)} positions'))

            # Create employees
            employees = self._create_employees(admin_user, positions, departments)
            self.stdout.write(self.style.SUCCESS(f'Created {len(employees)} employees'))

            # Create sales orders
            sales_orders = self._create_sales_orders(admin_user, customers, products)
            self.stdout.write(self.style.SUCCESS(f'Created {len(sales_orders)} sales orders'))

            # Create purchase orders
            purchase_orders = self._create_purchase_orders(admin_user, vendors, products)
            self.stdout.write(self.style.SUCCESS(f'Created {len(purchase_orders)} purchase orders'))

            # Create inventory transactions
            transactions = self._create_inventory_transactions(admin_user, products, warehouses)
            self.stdout.write(self.style.SUCCESS(f'Created {len(transactions)} inventory transactions'))

            # Create journal entries
            journal_entries = self._create_journal_entries(admin_user, accounts)
            self.stdout.write(self.style.SUCCESS(f'Created {len(journal_entries)} journal entries'))

            # Create payments
            payments = self._create_payments(admin_user, customers, vendors, sales_orders, purchase_orders)
            self.stdout.write(self.style.SUCCESS(f'Created {len(payments)} payments'))

            # Create invoices
            invoices = self._create_invoices(admin_user, customers, vendors, sales_orders, purchase_orders)
            self.stdout.write(self.style.SUCCESS(f'Created {len(invoices)} invoices'))

        self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))

    def _create_categories(self):
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic products and accessories'},
            {'name': 'Office Supplies', 'description': 'Office stationery and supplies'},
            {'name': 'Furniture', 'description': 'Office furniture and fixtures'},
            {'name': 'Raw Materials', 'description': 'Raw materials for production'},
            {'name': 'Services', 'description': 'Service offerings'},
        ]

        categories = []
        for data in categories_data:
            category, _ = Category.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            categories.append(category)

        return categories

    def _create_warehouses(self):
        warehouses_data = [
            {'name': 'Main Warehouse', 'address': '123 Main St, Anytown, USA'},
            {'name': 'East Warehouse', 'address': '456 East Ave, Eastville, USA'},
            {'name': 'West Warehouse', 'address': '789 West Blvd, Westville, USA'},
        ]

        warehouses = []
        for data in warehouses_data:
            warehouse, _ = Warehouse.objects.get_or_create(
                name=data['name'],
                defaults={'address': data['address']}
            )
            warehouses.append(warehouse)

        return warehouses

    def _create_products(self, categories):
        products_data = [
            {
                'sku': 'LT-001',
                'name': 'Laptop Pro',
                'description': 'High-performance laptop for professionals',
                'category': categories[0],  # Electronics
                'product_type': 'product',
                'unit_price': Decimal('1299.99'),
                'cost_price': Decimal('899.99'),
                'unit_of_measure': 'pcs',
                'barcode': '12345678901'
            },
            {
                'sku': 'PH-001',
                'name': 'Smartphone X',
                'description': 'Latest smartphone with advanced features',
                'category': categories[0],  # Electronics
                'product_type': 'product',
                'unit_price': Decimal('799.99'),
                'cost_price': Decimal('549.99'),
                'unit_of_measure': 'pcs',
                'barcode': '12345678902'
            },
            {
                'sku': 'PEN-001',
                'name': 'Ballpoint Pen',
                'description': 'Standard ballpoint pen - black ink',
                'category': categories[1],  # Office Supplies
                'product_type': 'product',
                'unit_price': Decimal('1.99'),
                'cost_price': Decimal('0.50'),
                'unit_of_measure': 'pcs',
                'barcode': '12345678903'
            },
            {
                'sku': 'PAPER-001',
                'name': 'A4 Paper',
                'description': '500 sheets of A4 paper',
                'category': categories[1],  # Office Supplies
                'product_type': 'product',
                'unit_price': Decimal('9.99'),
                'cost_price': Decimal('5.50'),
                'unit_of_measure': 'pack',
                'barcode': '12345678904'
            },
            {
                'sku': 'DESK-001',
                'name': 'Office Desk',
                'description': 'Standard office desk with drawers',
                'category': categories[2],  # Furniture
                'product_type': 'product',
                'unit_price': Decimal('299.99'),
                'cost_price': Decimal('189.99'),
                'unit_of_measure': 'pcs',
                'barcode': '12345678905'
            },
            {
                'sku': 'CHAIR-001',
                'name': 'Ergonomic Chair',
                'description': 'Ergonomic office chair with adjustable height',
                'category': categories[2],  # Furniture
                'product_type': 'product',
                'unit_price': Decimal('249.99'),
                'cost_price': Decimal('159.99'),
                'unit_of_measure': 'pcs',
                'barcode': '12345678906'
            },
            {
                'sku': 'RM-001',
                'name': 'Aluminum Sheet',
                'description': 'Raw aluminum sheet for production',
                'category': categories[3],  # Raw Materials
                'product_type': 'raw_material',
                'unit_price': Decimal('89.99'),
                'cost_price': Decimal('49.99'),
                'unit_of_measure': 'sheet',
                'barcode': '12345678907'
            },
            {
                'sku': 'SRV-001',
                'name': 'IT Support - Basic',
                'description': 'Basic IT support services - hourly rate',
                'category': categories[4],  # Services
                'product_type': 'service',
                'unit_price': Decimal('75.00'),
                'cost_price': Decimal('45.00'),
                'unit_of_measure': 'hour',
                'barcode': '12345678908'
            },
            {
                'sku': 'SRV-002',
                'name': 'IT Support - Premium',
                'description': 'Premium IT support services - hourly rate',
                'category': categories[4],  # Services
                'product_type': 'service',
                'unit_price': Decimal('125.00'),
                'cost_price': Decimal('75.00'),
                'unit_of_measure': 'hour',
                'barcode': '12345678909'
            },
            {
                'sku': 'RM-002',
                'name': 'Steel Rod',
                'description': 'Steel rod for manufacturing',
                'category': categories[3],  # Raw Materials
                'product_type': 'raw_material',
                'unit_price': Decimal('59.99'),
                'cost_price': Decimal('29.99'),
                'unit_of_measure': 'rod',
                'barcode': '12345678910'
            }
        ]

        products = []
        for data in products_data:
            product, _ = Product.objects.get_or_create(
                sku=data['sku'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'category': data['category'],
                    'product_type': data['product_type'],
                    'unit_price': data['unit_price'],
                    'cost_price': data['cost_price'],
                    'unit_of_measure': data['unit_of_measure'],
                    'barcode': data['barcode']
                }
            )
            products.append(product)

        return products

    def _create_inventory(self, products, warehouses):
        # Clear existing inventory data
        Inventory.objects.all().delete()

        # Create inventory records
        for product in products:
            if product.product_type == 'service':
                continue  # Skip services for inventory

            for warehouse in warehouses:
                quantity = random.randint(10, 100)
                reorder_point = random.randint(5, 20)

                Inventory.objects.create(
                    product=product,
                    warehouse=warehouse,
                    quantity_on_hand=quantity,
                    quantity_reserved=0,
                    quantity_available=quantity,
                    reorder_point=reorder_point,
                    reorder_quantity=reorder_point * 2
                )

        return Inventory.objects.all()

    def _create_customers(self, created_by):
        customers_data = [
            {
                'customer_code': 'CUST001',
                'name': 'Acme Corporation',
                'email': 'contact@acme.com',
                'phone': '555-123-4567',
                'address': '123 Business Ave',
                'city': 'Metropolis',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'customer_type': 'business',
                'credit_limit': Decimal('10000.00')
            },
            {
                'customer_code': 'CUST002',
                'name': 'TechSolutions Inc',
                'email': 'info@techsolutions.com',
                'phone': '555-987-6543',
                'address': '456 Tech Blvd',
                'city': 'Silicon Valley',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '94025',
                'customer_type': 'business',
                'credit_limit': Decimal('25000.00')
            },
            {
                'customer_code': 'CUST003',
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '555-555-1234',
                'address': '789 Residential St',
                'city': 'Anytown',
                'state': 'OH',
                'country': 'USA',
                'postal_code': '45678',
                'customer_type': 'individual',
                'credit_limit': Decimal('1000.00')
            },
            {
                'customer_code': 'CUST004',
                'name': 'City Government',
                'email': 'procurement@citygovt.gov',
                'phone': '555-777-8888',
                'address': '100 City Hall Plaza',
                'city': 'Govtown',
                'state': 'DC',
                'country': 'USA',
                'postal_code': '20001',
                'customer_type': 'government',
                'credit_limit': Decimal('50000.00')
            },
            {
                'customer_code': 'CUST005',
                'name': 'Global Enterprises Ltd',
                'email': 'sales@globalent.com',
                'phone': '555-333-9999',
                'address': '200 International Way',
                'city': 'Worldtown',
                'state': 'TX',
                'country': 'USA',
                'postal_code': '75001',
                'customer_type': 'business',
                'credit_limit': Decimal('30000.00')
            }
        ]

        customers = []
        for data in customers_data:
            customer, _ = Customer.objects.get_or_create(
                customer_code=data['customer_code'],
                defaults={
                    'name': data['name'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                    'postal_code': data['postal_code'],
                    'customer_type': data['customer_type'],
                    'credit_limit': data['credit_limit'],
                    'created_by': created_by
                }
            )
            customers.append(customer)

        return customers

    def _create_vendors(self, created_by):
        vendors_data = [
            {
                'vendor_code': 'VEND001',
                'name': 'Electronics Wholesale',
                'contact_person': 'Sarah Johnson',
                'email': 'sales@electronicswholesale.com',
                'phone': '555-111-2222',
                'address': '111 Supplier Road',
                'city': 'Suppliersville',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '90210',
                'vendor_type': 'supplier',
                'payment_terms': 'Net 30'
            },
            {
                'vendor_code': 'VEND002',
                'name': 'Office Depot',
                'contact_person': 'Michael Brown',
                'email': 'mbrown@officedepot.com',
                'phone': '555-222-3333',
                'address': '222 Office Way',
                'city': 'Officetown',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10002',
                'vendor_type': 'supplier',
                'payment_terms': 'Net 15'
            },
            {
                'vendor_code': 'VEND003',
                'name': 'Furniture Masters',
                'contact_person': 'David Wilson',
                'email': 'dwilson@furnituremasters.com',
                'phone': '555-333-4444',
                'address': '333 Furniture Ave',
                'city': 'Furntown',
                'state': 'MI',
                'country': 'USA',
                'postal_code': '48001',
                'vendor_type': 'supplier',
                'payment_terms': 'Net 45'
            },
            {
                'vendor_code': 'VEND004',
                'name': 'IT Consulting Services',
                'contact_person': 'Emma Davis',
                'email': 'emma@itconsulting.com',
                'phone': '555-444-5555',
                'address': '444 Tech Lane',
                'city': 'Techcity',
                'state': 'WA',
                'country': 'USA',
                'postal_code': '98001',
                'vendor_type': 'service_provider',
                'payment_terms': 'Net 15'
            },
            {
                'vendor_code': 'VEND005',
                'name': 'Building Contractors Inc',
                'contact_person': 'James Miller',
                'email': 'james@buildingcontractors.com',
                'phone': '555-555-6666',
                'address': '555 Construction Blvd',
                'city': 'Buildertown',
                'state': 'TX',
                'country': 'USA',
                'postal_code': '75002',
                'vendor_type': 'contractor',
                'payment_terms': 'Net 30'
            }
        ]

        vendors = []
        for data in vendors_data:
            vendor, _ = Vendor.objects.get_or_create(
                vendor_code=data['vendor_code'],
                defaults={
                    'name': data['name'],
                    'contact_person': data['contact_person'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                    'postal_code': data['postal_code'],
                    'vendor_type': data['vendor_type'],
                    'payment_terms': data['payment_terms'],
                    'created_by': created_by
                }
            )
            vendors.append(vendor)

        return vendors

    def _create_chart_of_accounts(self):
        accounts_data = [
            # Asset accounts
            {'account_code': '1000', 'account_name': 'Cash', 'account_type': 'asset'},
            {'account_code': '1100', 'account_name': 'Accounts Receivable', 'account_type': 'asset'},
            {'account_code': '1200', 'account_name': 'Inventory', 'account_type': 'asset'},
            {'account_code': '1300', 'account_name': 'Equipment', 'account_type': 'asset'},
            {'account_code': '1400', 'account_name': 'Buildings', 'account_type': 'asset'},
            {'account_code': '1500', 'account_name': 'Accumulated Depreciation', 'account_type': 'asset'},

            # Liability accounts
            {'account_code': '2000', 'account_name': 'Accounts Payable', 'account_type': 'liability'},
            {'account_code': '2100', 'account_name': 'Wages Payable', 'account_type': 'liability'},
            {'account_code': '2200', 'account_name': 'Long-term Debt', 'account_type': 'liability'},

            # Equity accounts
            {'account_code': '3000', 'account_name': 'Owner\'s Equity', 'account_type': 'equity'},
            {'account_code': '3100', 'account_name': 'Retained Earnings', 'account_type': 'equity'},

            # Revenue accounts
            {'account_code': '4000', 'account_name': 'Sales Revenue', 'account_type': 'revenue'},
            {'account_code': '4100', 'account_name': 'Service Revenue', 'account_type': 'revenue'},

            # Expense accounts
            {'account_code': '5000', 'account_name': 'Cost of Goods Sold', 'account_type': 'expense'},
            {'account_code': '5100', 'account_name': 'Salary Expense', 'account_type': 'expense'},
            {'account_code': '5200', 'account_name': 'Rent Expense', 'account_type': 'expense'},
            {'account_code': '5300', 'account_name': 'Utilities Expense', 'account_type': 'expense'},
            {'account_code': '5400', 'account_name': 'Depreciation Expense', 'account_type': 'expense'},
            {'account_code': '5500', 'account_name': 'Office Supplies Expense', 'account_type': 'expense'},
        ]

        accounts = []
        for data in accounts_data:
            account, _ = ChartOfAccounts.objects.get_or_create(
                account_code=data['account_code'],
                defaults={
                    'account_name': data['account_name'],
                    'account_type': data['account_type'],
                }
            )
            accounts.append(account)

        return accounts

    def _create_departments(self, manager):
        departments_data = [
            {'name': 'Sales', 'description': 'Sales and marketing department'},
            {'name': 'Finance', 'description': 'Finance and accounting department'},
            {'name': 'Operations', 'description': 'Operations and logistics department'},
            {'name': 'HR', 'description': 'Human resources department'},
            {'name': 'IT', 'description': 'Information technology department'},
        ]

        departments = []
        for data in departments_data:
            department, _ = Department.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'manager': manager
                }
            )
            departments.append(department)

        return departments

    def _create_positions(self, departments):
        positions_data = [
            {'title': 'Sales Manager', 'department': departments[0], 'min_salary': Decimal('60000'), 'max_salary': Decimal('90000')},
            {'title': 'Sales Representative', 'department': departments[0], 'min_salary': Decimal('40000'), 'max_salary': Decimal('60000')},
            {'title': 'Financial Controller', 'department': departments[1], 'min_salary': Decimal('70000'), 'max_salary': Decimal('100000')},
            {'title': 'Accountant', 'department': departments[1], 'min_salary': Decimal('50000'), 'max_salary': Decimal('70000')},
            {'title': 'Operations Manager', 'department': departments[2], 'min_salary': Decimal('65000'), 'max_salary': Decimal('95000')},
            {'title': 'Warehouse Supervisor', 'department': departments[2], 'min_salary': Decimal('45000'), 'max_salary': Decimal('65000')},
            {'title': 'HR Manager', 'department': departments[3], 'min_salary': Decimal('65000'), 'max_salary': Decimal('90000')},
            {'title': 'HR Specialist', 'department': departments[3], 'min_salary': Decimal('45000'), 'max_salary': Decimal('65000')},
            {'title': 'IT Manager', 'department': departments[4], 'min_salary': Decimal('75000'), 'max_salary': Decimal('110000')},
            {'title': 'Software Developer', 'department': departments[4], 'min_salary': Decimal('60000'), 'max_salary': Decimal('90000')},
        ]

        positions = []
        for data in positions_data:
            position, _ = Position.objects.get_or_create(
                title=data['title'],
                department=data['department'],
                defaults={
                    'min_salary': data['min_salary'],
                    'max_salary': data['max_salary']
                }
            )
            positions.append(position)

        return positions

    def _create_employees(self, admin_user, positions, departments):
        # Create additional users for employees
        users_data = [
            {'username': 'jsmith', 'email': 'jsmith@example.com', 'password': 'password123', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'mjones', 'email': 'mjones@example.com', 'password': 'password123', 'first_name': 'Mary', 'last_name': 'Jones'},
            {'username': 'rjohnson', 'email': 'rjohnson@example.com', 'password': 'password123', 'first_name': 'Robert', 'last_name': 'Johnson'},
            {'username': 'pwilliams', 'email': 'pwilliams@example.com', 'password': 'password123', 'first_name': 'Patricia', 'last_name': 'Williams'},
            {'username': 'jdoe', 'email': 'jdoe@example.com', 'password': 'password123', 'first_name': 'James', 'last_name': 'Doe'},
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
            users.append(user)

        # Add admin user to the list
        users.append(admin_user)

        # Create employees
        employees_data = [
            {'user': users[0], 'employee_id': 'EMP001', 'position': positions[1], 'department': departments[0], 'salary': Decimal('55000')},
            {'user': users[1], 'employee_id': 'EMP002', 'position': positions[3], 'department': departments[1], 'salary': Decimal('65000')},
            {'user': users[2], 'employee_id': 'EMP003', 'position': positions[5], 'department': departments[2], 'salary': Decimal('60000')},
            {'user': users[3], 'employee_id': 'EMP004', 'position': positions[7], 'department': departments[3], 'salary': Decimal('58000')},
            {'user': users[4], 'employee_id': 'EMP005', 'position': positions[9], 'department': departments[4], 'salary': Decimal('75000')},
            {'user': users[5], 'employee_id': 'EMP006', 'position': positions[0], 'department': departments[0], 'salary': Decimal('85000')},
        ]

        employees = []
        for data in employees_data:
            # Calculate a hire date in the past
            hire_date = timezone.now().date() - timedelta(days=random.randint(30, 365 * 3))

            employee, _ = Employee.objects.get_or_create(
                user=data['user'],
                defaults={
                    'employee_id': data['employee_id'],
                    'position': data['position'],
                    'department': data['department'],
                    'hire_date': hire_date,
                    'salary': data['salary'],
                    'employment_status': 'active',
                }
            )
            employees.append(employee)

        return employees

    def _create_sales_orders(self, created_by, customers, products):
        # Clear existing sales orders
        SalesOrder.objects.all().delete()

        # Create 10 sales orders with random items
        sales_orders = []
        for i in range(1, 11):
            # Pick a random customer
            customer = random.choice(customers)

            # Create an order with a recent date
            days_ago = random.randint(1, 60)
            order_date = timezone.now() - timedelta(days=days_ago)

            # Random status
            status_choices = ['draft', 'pending', 'confirmed', 'shipped', 'delivered', 'completed']
            status_weights = [0.1, 0.2, 0.2, 0.2, 0.2, 0.1]  # More weight to middle statuses
            status = random.choices(status_choices, weights=status_weights, k=1)[0]

            # Create the order
            order = SalesOrder.objects.create(
                order_number=f'SO{i:06d}',
                customer=customer,
                order_date=order_date,
                status=status,
                notes=f'Sample sales order {i}',
                created_by=created_by
            )

            # Add 1-5 random products to the order
            subtotal = Decimal('0')
            num_items = random.randint(1, 5)

            for _ in range(num_items):
                # Pick a random product (excluding services for simplicity)
                product = random.choice([p for p in products if p.product_type != 'service'])

                # Random quantity and optional discount
                quantity = random.randint(1, 10)
                discount_percent = random.choice([0, 0, 0, 5, 10])  # 60% chance of no discount

                # Add the item
                item = SalesOrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    discount_percent=discount_percent
                )

                # Update order subtotal
                subtotal += item.line_total

            # Calculate tax and total
            tax_rate = Decimal('0.08')  # 8% tax rate
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount

            # Update the order with calculated totals
            order.subtotal = subtotal
            order.tax_amount = tax_amount
            order.total_amount = total_amount
            order.save()

            sales_orders.append(order)

        return sales_orders

    def _create_purchase_orders(self, created_by, vendors, products):
        # Clear existing purchase orders
        PurchaseOrder.objects.all().delete()

        # Get first warehouse for purchase orders
        warehouses = Warehouse.objects.all()
        if not warehouses.exists():
            self.stdout.write(self.style.WARNING('No warehouses found, skipping purchase orders'))
            return []

        # Create 8 purchase orders with random items
        purchase_orders = []
        for i in range(1, 9):
            # Pick a random vendor
            vendor = random.choice(vendors)
            warehouse = random.choice(warehouses)

            # Create an order with a recent date
            days_ago = random.randint(1, 60)
            order_date = timezone.now() - timedelta(days=days_ago)

            # Random status - fix the status choices to match model
            status_choices = ['draft', 'pending', 'confirmed', 'received', 'completed']
            status_weights = [0.1, 0.2, 0.3, 0.2, 0.2]
            status = random.choices(status_choices, weights=status_weights, k=1)[0]

            # Create the order
            order = PurchaseOrder.objects.create(
                po_number=f'PO{i:06d}',
                vendor=vendor,
                warehouse=warehouse,
                status=status,
                notes=f'Sample purchase order {i}',
                created_by=created_by
            )

            # Add 1-5 random products to the order
            num_items = random.randint(1, 5)

            for _ in range(num_items):
                # Pick a random product (excluding services for simplicity)
                product = random.choice([p for p in products if p.product_type != 'service'])

                # Random quantity
                quantity = random.randint(5, 50)

                # Add the item - use correct field name unit_price
                PurchaseOrderItem.objects.create(
                    purchase_order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.cost_price
                )

            # Calculate totals using model method
            order.calculate_totals()

            purchase_orders.append(order)

        return purchase_orders

    def _create_inventory_transactions(self, created_by, products, warehouses):
        # Clear existing inventory transactions
        InventoryTransaction.objects.all().delete()

        # Create 30 random inventory transactions
        transactions = []
        for i in range(30):
            # Pick a random product (excluding services)
            product = random.choice([p for p in products if p.product_type != 'service'])

            # Pick a random warehouse
            warehouse = random.choice(warehouses)

            # Random transaction type
            transaction_type = random.choice(['in', 'out', 'transfer', 'adjustment', 'return'])

            # Random quantity
            if transaction_type in ['in', 'return']:
                quantity = random.randint(5, 50)
            else:
                quantity = random.randint(1, 10)

            # Random date in the past 60 days
            days_ago = random.randint(1, 60)
            transaction_date = timezone.now() - timedelta(days=days_ago)

            # Create the transaction
            transaction = InventoryTransaction.objects.create(
                transaction_type=transaction_type,
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reference_number=f'TR{i+1:06d}',
                notes=f'Sample inventory transaction {i+1}',
                created_by=created_by,
                created_at=transaction_date
            )

            transactions.append(transaction)

        return transactions

    def _create_journal_entries(self, created_by, accounts):
        # Clear existing journal entries
        JournalEntry.objects.all().delete()

        # Create 15 journal entries
        journal_entries = []
        for i in range(1, 16):
            # Random date in the past 60 days
            days_ago = random.randint(1, 60)
            entry_date = (timezone.now() - timedelta(days=days_ago)).date()

            # Create the journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=f'JE{i:06d}',
                date=entry_date,
                description=f'Sample journal entry {i}',
                entry_type='manual',
                is_posted=True,
                created_by=created_by
            )

            # Add 2-4 journal lines
            total_debit = Decimal('0')
            total_credit = Decimal('0')

            # Random transaction amount between $100 and $10,000
            transaction_amount = Decimal(str(random.uniform(100, 10000))).quantize(Decimal('0.01'))

            # First line - debit an asset/expense account
            debit_account = random.choice([a for a in accounts if a.account_type in ['asset', 'expense']])
            JournalLine.objects.create(
                journal=journal_entry,
                account=debit_account,
                description=f'Debit to {debit_account.account_name}',
                debit=transaction_amount,
                credit=Decimal('0')
            )
            total_debit += transaction_amount

            # Second line - credit a liability/equity/revenue account
            credit_account = random.choice([a for a in accounts if a.account_type in ['liability', 'equity', 'revenue']])
            JournalLine.objects.create(
                journal=journal_entry,
                account=credit_account,
                description=f'Credit to {credit_account.account_name}',
                debit=Decimal('0'),
                credit=transaction_amount
            )
            total_credit += transaction_amount

            # Update journal entry totals
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()

            journal_entries.append(journal_entry)

        return journal_entries

    def _create_payments(self, created_by, customers, vendors, sales_orders, purchase_orders):
        # Clear existing payments
        Payment.objects.all().delete()

        payments = []
        
        # Create customer payments (receipts)
        for i, customer in enumerate(customers[:3]):  # Create payments for first 3 customers
            payment = Payment.objects.create(
                payment_number=f'PAY{i+1:06d}',
                payment_type='receipt',
                amount=Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01')),
                payment_method=random.choice(['cash', 'check', 'bank_transfer', 'credit_card']),
                reference_number=f'REF{i+1:06d}',
                customer=customer,
                notes=f'Payment from {customer.name}',
                created_by=created_by
            )
            payments.append(payment)

        # Create vendor payments
        for i, vendor in enumerate(vendors[:3]):  # Create payments for first 3 vendors
            payment = Payment.objects.create(
                payment_number=f'PAY{i+4:06d}',
                payment_type='payment',
                amount=Decimal(str(random.uniform(200, 3000))).quantize(Decimal('0.01')),
                payment_method=random.choice(['check', 'bank_transfer']),
                reference_number=f'REF{i+4:06d}',
                vendor=vendor,
                notes=f'Payment to {vendor.name}',
                created_by=created_by
            )
            payments.append(payment)

        return payments

    def _create_invoices(self, created_by, customers, vendors, sales_orders, purchase_orders):
        # Clear existing invoices
        Invoice.objects.all().delete()

        invoices = []
        
        # Create sales invoices
        for i, order in enumerate(sales_orders[:5]):  # Create invoices for first 5 sales orders
            invoice = Invoice.objects.create(
                invoice_number=f'INV{i+1:06d}',
                invoice_type='sales',
                status=random.choice(['draft', 'sent', 'paid']),
                invoice_date=(timezone.now() - timedelta(days=random.randint(1, 30))).date(),
                due_date=(timezone.now() + timedelta(days=random.randint(15, 45))).date(),
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                paid_amount=order.total_amount if random.choice([True, False]) else Decimal('0'),
                customer=order.customer,
                sales_order=order,
                notes=f'Invoice for sales order {order.order_number}',
                created_by=created_by
            )
            invoices.append(invoice)

        # Create purchase invoices
        for i, order in enumerate(purchase_orders[:3]):  # Create invoices for first 3 purchase orders
            invoice = Invoice.objects.create(
                invoice_number=f'INV{i+6:06d}',
                invoice_type='purchase',
                status=random.choice(['draft', 'sent', 'paid']),
                invoice_date=(timezone.now() - timedelta(days=random.randint(1, 30))).date(),
                due_date=(timezone.now() + timedelta(days=random.randint(15, 45))).date(),
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                paid_amount=order.total_amount if random.choice([True, False]) else Decimal('0'),
                vendor=order.vendor,
                purchase_order=order,
                notes=f'Invoice for purchase order {order.po_number}',
                created_by=created_by
            )
            invoices.append(invoice)

        return invoices
