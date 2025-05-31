from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product

def catalog(request):
    products = Product.objects.all()
    return render(request, 'catalog/catalog.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        messages.success(request, f'Добавлено {quantity} шт. {product.name} (размер {size}) в корзину!')
        return redirect('product_detail', product_id=product_id)
    return render(request, 'catalog/product_detail.html', {'product': product})