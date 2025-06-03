import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from catalog.models import Product, Size
from .models import CartItem

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_name = request.POST.get('size')
    color = request.POST.get('color')
    quantity = int(request.POST.get('quantity', 1))

    if not size_name:
        return JsonResponse({'success': False, 'error': 'Пожалуйста, выберите размер.'}, status=400)

    size = get_object_or_404(Size, name=size_name)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'Товар {product.name} добавлен в корзину!',
        'product_id': product_id
    })

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'size')
    total_price = sum(item.get_total_price() for item in cart_items)
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'cart/cart.html', context)

@login_required
@require_POST
def update_quantity(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, user=request.user)
        data = json.loads(request.body)
        new_quantity = data.get('quantity', item.quantity)
        print(f"Обновление item_id: {item_id}, new_quantity: {new_quantity}")

        if new_quantity < 1:
            return JsonResponse({'success': False, 'error': 'Количество не может быть меньше 1'}, status=400)

        item.quantity = new_quantity
        item.save()

        total_price = sum(item.get_total_price() for item in CartItem.objects.filter(user=request.user))
        print(f"Total price: {total_price}, Item count: {CartItem.objects.filter(user=request.user).count()}")
        return JsonResponse({
            'success': True,
            'item_total_price': item.get_total_price(),
            'total_price': total_price,
            'item_count': CartItem.objects.filter(user=request.user).count()
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def remove_item(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, user=request.user)
        print(f"Удаление item_id: {item_id}")
        item.delete()
        total_price = sum(item.get_total_price() for item in CartItem.objects.filter(user=request.user))
        print(f"Total price: {total_price}, Item count: {CartItem.objects.filter(user=request.user).count()}")
        return JsonResponse({
            'success': True,
            'total_price': total_price,
            'item_count': CartItem.objects.filter(user=request.user).count()
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)