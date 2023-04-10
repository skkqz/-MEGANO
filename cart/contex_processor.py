from .service import Cart


def cart(request):
    # cart = Cart(request)
    # quantity = cart.get_total_quantity
    return {'cart': Cart(request)}
