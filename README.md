# Coca-Cola Enterprise Management System

A comprehensive web-based management system designed to centralize and streamline all core business operations for Coca-Cola under one platform.

## Overview

This enterprise solution integrates multiple operational modules to manage employees, production, sales, inventory, finances, logistics, marketing, and sustainability efforts. The application is built using Django on the backend with HTML, CSS, and JavaScript for a responsive frontend experience.

## Features

### Employee Management
- Staff registration and profile management
- Job title and department assignment
- Attendance tracking
- Leave application processing
- Payroll generation
- Performance evaluations

### Product Management
- Product catalog maintenance
- Ingredient and formulation tracking
- Packaging types management
- Pricing administration
- Quality control records
- Product lifecycle tracking

### Inventory and Supply Chain
- Real-time stock monitoring
- Warehouse management
- Delivery tracking
- Supplier information
- Purchase order processing
- Procurement workflows

### Sales and Distribution
- Order management
- Invoice generation
- Delivery scheduling
- Performance analytics
- Logistics route optimization
- Order fulfillment tracking

### Finance and Accounting
- Budget management
- Revenue and expense tracking
- Journal entries
- Financial reporting
- Tax management
- Payment integrations

### Marketing Campaign Management
- Campaign setup and tracking
- Media asset management
- Promotional QR code generation
- Campaign performance analytics
- Regional content management

### Customer and Retail Partner CRM
- Partner onboarding
- Communication history
- Loyalty program administration
- Support ticketing system

### Production Line Monitoring
- Real-time efficiency tracking
- Downtime incident logging
- Production output monitoring
- Maintenance scheduling
- Productivity reporting

### Sustainability and Compliance
- Environmental impact tracking
- Resource consumption monitoring
- Recycling statistics
- Compliance reporting

### Reporting and Dashboard
- Real-time KPI visualization
- Custom charts and analytics
- Department-specific insights
- Excel/PDF export functionality
- Automated report scheduling

## Technical Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Authentication**: Django's built-in authentication with custom role-based permissions

## Role-Based Access

The system supports various user roles including:
- Super Admin
- HR Manager
- Plant Manager
- Finance Officer
- Sales Executive
- Distributor
- Retail Partner

Each role has tailored access to specific modules and data relevant to their responsibilities.

## Installation

1. Clone the repository
   ```
   git clone https://github.com/coca-cola/enterprise-management-system.git
   cd enterprise-management-system
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Configure the database in settings.py

5. Apply migrations
   ```
   python manage.py migrate
   ```

6. Create a superuser
   ```
   python manage.py createsuperuser
   ```

7. Run the development server
   ```
   python manage.py runserver
   ```

## Development

When contributing to this project, please follow the established coding standards and ensure all tests pass before submitting pull requests.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Support

For technical support or feature requests, please contact the IT department or open an issue in the internal ticketing system.