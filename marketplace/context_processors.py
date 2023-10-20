from .models import Cart, Tax

from menu.models import FoodItem


# get cart  count
def get_cart_counter(request):
    cart_count = 0

    # check user logged
    if request.user.is_authenticated:
        try:
            # get cart items
            cart_items = Cart.objects.filter(user=request.user)

            # forloop
            if cart_items:
                for cart_item in cart_items:
                    # cart count
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0

    return dict(cart_count=cart_count)


# get count amounts
def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    total = 0
    grand_total = 0
    tax_dict = {}

    if request.user.is_authenticated:
        # get cart items
        cart_items = Cart.objects.filter(user=request.user)

        # for loop get item
        for item in cart_items:
            # get item
            food_item = FoodItem.objects.get(pk=item.food_item.id)
            # calc subtotal
            subtotal += (food_item.price * item.quantity)

        # get tax
        get_tax = Tax.objects.filter(is_active=True)

        # for loop
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage*subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        tax = sum(x for key in tax_dict.values() for x in key.values())

        print(tax)

        grand_total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
