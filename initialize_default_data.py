#!/usr/bin/env python
"""
Script to add default warehouses and positions to the database.
Run this script to initialize some basic data for your ERP system.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ERP_PROJECT.settings')
django.setup()

from erpdb.models import Warehouse, Department, Position
from django.db import transaction
from django.contrib.auth.models import User

def create_default_warehouses():
    """Create default warehouses if they don't exist"""
    warehouses = [
        {
            'name': 'Main Warehouse',
            'address': 'Block 123, Main Street',
            'city': 'Manila',
            'state': 'Metro Manila',
            'country': 'Philippines',
            'postal_code': '1000',
            'contact_person': 'John Doe',
            'phone': '+63 912 345 6789',
            'email': 'warehouse@litework.com'
        },
        {
            'name': 'South Distribution Center',
            'address': 'Block 456, South Avenue',
            'city': 'Cebu',
            'state': 'Cebu',
            'country': 'Philippines',
            'postal_code': '6000',
            'contact_person': 'Jane Smith',
            'phone': '+63 923 456 7890',
            'email': 'south.dc@litework.com'
        },
        {
            'name': 'North Distribution Center',
            'address': 'Block 789, North Boulevard',
            'city': 'Baguio',
            'state': 'Benguet',
            'country': 'Philippines',
            'postal_code': '2600',
            'contact_person': 'Mark Johnson',
            'phone': '+63 934 567 8901',
            'email': 'north.dc@litework.com'
        },
    ]

    for warehouse_data in warehouses:
        Warehouse.objects.get_or_create(
            name=warehouse_data['name'],
            defaults=warehouse_data
        )

    print(f"✓ Created {len(warehouses)} default warehouses")

def create_default_departments():
    """Create default departments if they don't exist"""
    departments = [
        {
            'name': 'Sales',
            'description': 'Responsible for sales activities and customer relationships'
        },
        {
            'name': 'Marketing',
            'description': 'Handles marketing campaigns and brand management'
        },
        {
            'name': 'Finance',
            'description': 'Manages financial operations and reporting'
        },
        {
            'name': 'Human Resources',
            'description': 'Responsible for recruitment and employee management'
        },
        {
            'name': 'Operations',
            'description': 'Manages day-to-day business operations'
        },
        {
            'name': 'IT',
            'description': 'Handles technical infrastructure and software'
        },
    ]

    created_departments = []
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults=dept_data
        )
        created_departments.append(dept)

    print(f"✓ Created {len(created_departments)} default departments")
    return created_departments

def create_default_positions(departments):
    """Create default positions for each department if they don't exist"""
    positions = [
        # Sales positions
        {
            'title': 'Sales Manager',
            'department': 'Sales',
            'description': 'Oversees the sales team and strategies',
            'min_salary': 70000,
            'max_salary': 95000
        },
        {
            'title': 'Sales Representative',
            'department': 'Sales',
            'description': 'Responsible for direct sales to clients',
            'min_salary': 40000,
            'max_salary': 65000
        },

        # Marketing positions
        {
            'title': 'Marketing Director',
            'department': 'Marketing',
            'description': 'Leads marketing efforts and strategy',
            'min_salary': 75000,
            'max_salary': 100000
        },
        {
            'title': 'Marketing Specialist',
            'department': 'Marketing',
            'description': 'Implements marketing campaigns',
            'min_salary': 45000,
            'max_salary': 65000
        },

        # Finance positions
        {
            'title': 'Financial Analyst',
            'department': 'Finance',
            'description': 'Analyzes financial data and prepares reports',
            'min_salary': 55000,
            'max_salary': 80000
        },
        {
            'title': 'Accountant',
            'department': 'Finance',
            'description': 'Manages accounting and bookkeeping',
            'min_salary': 50000,
            'max_salary': 75000
        },

        # HR positions
        {
            'title': 'HR Manager',
            'department': 'Human Resources',
            'description': 'Oversees HR functions and policies',
            'min_salary': 65000,
            'max_salary': 90000
        },
        {
            'title': 'HR Specialist',
            'department': 'Human Resources',
            'description': 'Handles recruitment and employee relations',
            'min_salary': 45000,
            'max_salary': 65000
        },

        # Operations positions
        {
            'title': 'Operations Manager',
            'department': 'Operations',
            'description': 'Manages operational activities',
            'min_salary': 70000,
            'max_salary': 95000
        },
        {
            'title': 'Logistics Coordinator',
            'department': 'Operations',
            'description': 'Coordinates shipping and receiving',
            'min_salary': 45000,
            'max_salary': 65000
        },

        # IT positions
        {
            'title': 'IT Manager',
            'department': 'IT',
            'description': 'Oversees IT infrastructure and team',
            'min_salary': 80000,
            'max_salary': 110000
        },
        {
            'title': 'Software Developer',
            'department': 'IT',
            'description': 'Develops and maintains software applications',
            'min_salary': 65000,
            'max_salary': 95000
        },
    ]

    # Create a department lookup for faster access
    dept_lookup = {dept.name: dept for dept in departments}

    position_count = 0
    for pos_data in positions:
        dept_name = pos_data.pop('department')
        if dept_name in dept_lookup:
            pos_data['department'] = dept_lookup[dept_name]
            Position.objects.get_or_create(
                title=pos_data['title'],
                department=pos_data['department'],
                defaults=pos_data
            )
            position_count += 1

    print(f"✓ Created {position_count} default positions")

@transaction.atomic
def initialize_default_data():
    """Initialize all default data"""
    print("Initializing default data for ERP system...")

    # Create warehouses, departments, and positions
    create_default_warehouses()
    departments = create_default_departments()
    create_default_positions(departments)

    print("Default data initialization complete!")

if __name__ == "__main__":
    initialize_default_data()
