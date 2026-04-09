# Django Online Store for Wasmer Deployment

A complete Django-based online store frontend designed for hosting on Wasmer, featuring a comprehensive admin panel for managing an e-commerce business.

## Features

### Customer-Facing Features
- **Home Page**: Displays featured products, latest arrivals, and category browsing
- **Product Catalog**: Browse products with filtering by category, search, and sorting options
- **Product Details**: Detailed product pages with related products and customer reviews
- **Shopping Cart**: Session-based cart management
- **Checkout**: Guest checkout with shipping and billing information
- **Order History**: Registered users can view their order history
- **Responsive Design**: Mobile-friendly interface with the brand colors

### Admin Panel Features
- **Category Management**: Add, edit, and delete product categories
- **Product Listing**: Full CRUD operations for products with image upload
- **Discount Management**: Create time-limited discounts with percentage-based pricing
- **Order Processing**: View, filter, and update order status (pending → confirmed → processing → shipped → delivered)
- **Customer Reviews**: Approve or reject customer reviews
- **Bulk Actions**: Update multiple orders at once

## Brand Colors
- **Primary Color**: #FE9202 (Orange)
- **Secondary Color**: #002060 (Navy Blue)

## Tech Stack
- Django 6.0
- SQLite (default, can be changed for production)
- Pillow for image handling
- Session-based cart system

## Project Structure

```
/workspace/
├── manage.py
├── store/                  # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── admin.py           # Admin configuration
│   ├── urls.py            # URL routing
│   ├── templates/shop/    # HTML templates
│   └── static/css/        # Static files
├── media/                 # Uploaded media files
└── staticfiles/           # Collected static files
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install django pillow wasmer
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Storefront**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

## Admin Usage

1. Log in to the admin panel at `/admin/`
2. Use the navigation to manage:
   - **Categories**: Create product categories
   - **Products**: Add products with images, prices, and stock levels
   - **Discounts**: Set up promotional discounts
   - **Orders**: Process customer orders through various stages

## Wasmer Deployment

This project is configured for deployment on Wasmer. Key considerations:

1. **Static Files**: Run `python manage.py collectstatic` before deployment
2. **Database**: Configure production database settings in `settings.py`
3. **Media Files**: Ensure proper storage configuration for uploaded images
4. **Environment Variables**: Set `SECRET_KEY`, `DEBUG=False`, and `ALLOWED_HOSTS`

## Models

- **Category**: Product categorization
- **Product**: Store items with pricing and inventory
- **ProductImage**: Additional product images
- **Discount**: Time-limited promotional offers
- **Order**: Customer orders with status tracking
- **OrderItem**: Individual items within orders
- **CustomerReview**: Product reviews and ratings

## License

This project is created for the startup business and is proprietary.
