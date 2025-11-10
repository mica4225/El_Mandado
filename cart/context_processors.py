def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = cart.cantidad_items()
        except:
            count = 0
    else:
        count = 0
    
    return {'cart_count': count}