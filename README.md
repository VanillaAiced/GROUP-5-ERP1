# LiteWork-ERP

A comprehensive Enterprise Resource Planning (ERP) system built with Django, designed to manage all aspects of business operations from customer relations to financial reporting.

## 🚀 Features

### Core Modules

#### 1. Customer Relationship Management (CRM)
- **Customer Management**: Complete customer profiles with contact information, credit limits, and payment terms
- **Vendor Management**: Supplier and vendor relationship management
- **Customer Types**: Support for individual, business, and government customers
- **Address Management**: Full address tracking with city, state, country, and postal codes

#### 2. Sales & Marketing
- **Sales Orders**: Complete sales order management with status tracking
- **Product Catalog**: Comprehensive product management with categories and variants
- **Pricing Management**: Flexible pricing with discount support
- **Order Processing**: Multi-step order workflow (Draft → Pending → Confirmed → Shipped → Delivered)

#### 3. Procurement & Inventory
- **Purchase Orders**: Vendor purchase order management
- **Inventory Management**: Real-time stock tracking across multiple warehouses
- **Stock Transactions**: Complete audit trail of all inventory movements
- **Reorder Management**: Automated low-stock alerts and reorder point tracking
- **Warehouse Management**: Multi-location inventory support

#### 4. Human Resources
- **Employee Management**: Complete employee profiles and records
- **Department Management**: Organizational structure management
- **Position Management**: Job roles and salary ranges
- **Employment Status**: Track active, inactive, terminated, and on-leave employees

#### 5. Finance & Accounting
- **Chart of Accounts**: Flexible account structure
- **Journal Entries**: Double-entry bookkeeping system
- **Financial Reports**: Balance sheet, income statement, cash flow, and trial balance
- **Sales Reporting**: Comprehensive sales analytics and reporting

#### 6. Reporting & Analytics
- **Dashboard**: Real-time business metrics and KPIs
- **Financial Reports**: Automated financial statement generation
- **Inventory Reports**: Stock valuation and movement reports
- **Sales Analytics**: Customer and product performance analysis

## 🏗️ Technical Architecture

### Database Models
- **Enhanced Data Models**: UUID primary keys, audit trails, and comprehensive relationships
- **Inventory Tracking**: Real-time stock levels with reserved quantities
- **Financial Integrity**: Double-entry bookkeeping with validation
- **User Management**: Integration with Django's authentication system

### Business Logic
- **Service Layer**: Clean separation of business logic from views
- **Transaction Management**: Atomic operations for data consistency
- **Validation**: Comprehensive data validation and business rules
- **Notifications**: Automated alerts for low stock and other business events

### User Interface
- **Modern Dashboard**: Clean, responsive design with Tailwind CSS
- **Modular Navigation**: Organized by business function
- **Real-time Updates**: Live data updates and notifications
- **Mobile Responsive**: Works on all device sizes

## 📁 Project Structure

```
GROUP-5-ERP/
├── authentication/          # User authentication and registration
├── dashboard/               # Main dashboard views and templates
├── erpdb/                   # Core ERP models, views, and business logic
│   ├── models.py           # Database models
│   ├── views.py            # Business views and API endpoints
│   ├── forms.py            # Django forms for data entry
│   ├── admin.py            # Django admin configuration
│   ├── services.py         # Business logic services
│   └── urls.py             # URL routing
├── ERP_PROJECT/            # Django project settings
├── templates/              # HTML templates
├── staticfiles/            # Static assets (CSS, JS, images)
└── requirements.txt        # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GROUP-5-ERP
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**:
   - Create a PostgreSQL database named `erp`
   - Update database credentials in `ERP_PROJECT/settings.py`

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data** (optional):
   ```bash
   python manage.py loaddata initial_data.json
   ```

8. **Start development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   - Main application: `http://127.0.0.1:8000/`
   - Admin interface: `http://127.0.0.1:8000/admin/`

## 🎯 Usage Guide

### Getting Started
1. **Login**: Use your superuser credentials to access the system
2. **Dashboard**: View key business metrics and recent activities
3. **Navigation**: Use the sidebar to access different modules

### Key Workflows

#### Customer Management
1. Navigate to **Customers** in the CRM section
2. Click **Add Customer** to create new customer profiles
3. View customer details, sales history, and credit information

#### Sales Process
1. Go to **Sales Orders** in the Sales & Marketing section
2. Create new sales orders with customer and product information
3. Process orders through the workflow stages
4. Monitor order status and fulfillment

#### Inventory Management
1. Access **Inventory** in the Procurement section
2. View current stock levels across all warehouses
3. Create inventory transactions for stock movements
4. Set up reorder points for automatic alerts

#### Financial Reporting
1. Navigate to **Reports** in the Finance section
2. Generate financial statements and reports
3. View sales analytics and performance metrics

## 🔧 Configuration

### Database Configuration
Update `ERP_PROJECT/settings.py` with your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'erp',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email Configuration
Configure email settings for notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS` with your domain
3. Set up proper database credentials
4. Configure static file serving
5. Set up SSL certificates

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🚀 Heroku Deployment

You can deploy this project to Heroku with a single command using the provided deployment script. This will:
- Check prerequisites (Git, Heroku CLI)
- Initialize a git repository (if needed)
- Create a Heroku app (if needed)
- Add Heroku Postgres
- Set essential environment variables (SECRET_KEY, DEBUG)
- Push your code to Heroku
- Run migrations
- Optionally create a Django superuser
- Open your deployed app in the browser

### Steps

1. **Install prerequisites:**
   - [Git](https://git-scm.com/download/windows)
   - [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
   - Python 3.8+

2. **Run the deployment script:**
   ```cmd
   deploy_to_heroku.bat
   ```
   - Follow the prompts to set your SECRET_KEY and create a superuser if desired.

3. **Set additional environment variables (optional):**
   If you use email or S3 features, set these in the Heroku dashboard or via CLI:
   ```cmd
   heroku config:set EMAIL_HOST_USER=your_email@gmail.com EMAIL_HOST_PASSWORD=your_app_password
   heroku config:set USE_S3=True AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_STORAGE_BUCKET_NAME=...
   ```

4. **Access your app:**
   The script will open your deployed app in your browser. You can also run:
   ```cmd
   heroku open
   ```

5. **Troubleshooting:**
   - Check logs with: `heroku logs --tail`
   - Ensure all required environment variables are set for production

## 📊 API Endpoints

The system provides REST API endpoints for external integrations:

- `GET /erp/api/customer/<uuid>/` - Get customer data
- `GET /erp/api/product/<uuid>/` - Get product information
- `GET /erp/api/inventory/<uuid>/<warehouse_id>/` - Get inventory data

## 🔒 Security Features

- **User Authentication**: Django's built-in authentication system
- **Permission Management**: Role-based access control
- **Data Validation**: Comprehensive input validation
- **Audit Trails**: Track all data changes and user actions
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **CSRF Protection**: Cross-site request forgery protection

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core ERP functionality
- **v1.1.0** - Added comprehensive reporting and analytics
- **v1.2.0** - Enhanced inventory management and notifications

---

**Built with ❤️ using Django and modern web technologies**
