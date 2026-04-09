from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for store items"""
    category = models.ForeignKey(
        Category, 
        related_name='products', 
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    images = models.ManyToManyField(
        'ProductImage', 
        related_name='products', 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        """Calculate price after discount"""
        discount = self.discounts.filter(is_active=True).first()
        if discount:
            return self.price * (1 - discount.percentage / 100)
        return self.price

    @property
    def has_discount(self):
        """Check if product has active discount"""
        return self.discounts.filter(is_active=True).exists()


class ProductImage(models.Model):
    """Additional images for products"""
    product = models.ForeignKey(
        Product, 
        related_name='product_images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='products/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Discount(models.Model):
    """Discount model for products"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Discount percentage (e.g., 20.00 for 20%)"
    )
    products = models.ManyToManyField(
        Product, 
        related_name='discounts',
        blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.percentage}%"


class Order(models.Model):
    """Customer order model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        User, 
        related_name='orders', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # For guest checkout
    guest_email = models.EmailField(blank=True)
    guest_first_name = models.CharField(max_length=100, blank=True)
    guest_last_name = models.CharField(max_length=100, blank=True)
    
    shipping_address = models.TextField()
    billing_address = models.TextField()
    phone = models.CharField(max_length=20)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.get_customer_name()}"

    def get_customer_name(self):
        if self.customer:
            return self.customer.get_full_name() or self.customer.username
        return f"{self.guest_first_name} {self.guest_last_name}"


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(
        Order, 
        related_name='items', 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        related_name='order_items', 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity * (1 - self.discount / 100)
        super().save(*args, **kwargs)


class CustomerReview(models.Model):
    """Customer reviews for products"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(
        Product, 
        related_name='reviews', 
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        User, 
        related_name='reviews', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    guest_name = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.get_reviewer_name()}"

    def get_reviewer_name(self):
        if self.customer:
            return self.customer.get_full_name() or self.customer.username
        return self.guest_name
