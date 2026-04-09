from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Category, Product, Discount, Order, OrderItem


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'shop/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            is_featured=True
        )[:8]
        context['latest_products'] = Product.objects.filter(
            is_active=True
        ).order_by('-created_at')[:8]
        context['categories'] = Category.objects.all()
        return context


class ProductListView(ListView):
    """Product listing view"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            )
        
        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['sort_options'] = [
            ('-created_at', 'Newest'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('name', 'Name: A to Z'),
        ]
        return context


class ProductDetailView(DetailView):
    """Product detail view"""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        context['reviews'] = product.reviews.filter(is_approved=True)
        return context


class CategoryListView(ListView):
    """Category listing view"""
    model = Category
    template_name = 'shop/category_list.html'
    context_object_name = 'categories'


def cart_view(request):
    """Shopping cart view"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id, is_active=True)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@require_POST
def add_to_cart(request):
    """Add product to cart"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': sum(cart.values())})
    
    return redirect('cart')


@require_POST
def update_cart(request):
    """Update cart item quantity"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 0))
    
    cart = request.session.get('cart', {})
    
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('cart')


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    product_id = request.POST.get('product_id')
    cart = request.session.get('cart', {})
    cart.pop(product_id, None)
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('cart')


def checkout_view(request):
    """Checkout view"""
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')
        notes = request.POST.get('notes')
        
        # Get cart items
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart')
        
        # Calculate totals
        total_amount = 0
        order_items = []
        
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id, is_active=True)
            discount = product.discounts.filter(is_active=True).first()
            discount_percent = discount.percentage if discount else 0
            subtotal = product.price * quantity * (1 - discount_percent / 100)
            total_amount += subtotal
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price,
                'discount': discount_percent,
                'subtotal': subtotal
            })
        
        # Create order
        order = Order.objects.create(
            guest_email=email,
            guest_first_name=first_name,
            guest_last_name=last_name,
            phone=phone,
            shipping_address=shipping_address,
            billing_address=billing_address,
            total_amount=total_amount,
            final_amount=total_amount,
            notes=notes,
            status='pending'
        )
        
        # Create order items
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
                discount=item['discount'],
                subtotal=item['subtotal']
            )
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        return render(request, 'shop/order_confirmation.html', {'order': order})
    
    # GET request - show checkout form
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')
    
    return render(request, 'shop/checkout.html')


@login_required
def order_history_view(request):
    """User's order history"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


def search_view(request):
    """Search products"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        is_active=True,
        name__icontains=query
    ) | Product.objects.filter(
        is_active=True,
        description__icontains=query
    )
    return render(request, 'shop/search_results.html', {
        'products': products,
        'query': query
    })
