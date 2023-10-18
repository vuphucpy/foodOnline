$(document).ready(function(){
    // add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault()
        
        // food id
        food_id = $(this).attr('data-id')
        // url
        url = $(this).attr('data-url')
        
        // ajax
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status == 'Login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login';
                    })
                } if (response.status == 'Failed'){
                    swal(response.message,'','error')
                } if (response.status == 'Success'){
                    swal(response.message,'','success')
                    // load cart counter and quantity realtime
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // subtotal, tax and grand total
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total'],
                    )
                }
            }
        })
    })

    // place the cart item quantity on load
    $('.item_qty').each(function(){
        let the_id = $(this).attr('id')
        let qty = $(this).attr('data-qty')

        // load qty
        $('#'+the_id).html(qty)
    })

    // decrease cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault()
        
        // food id
        food_id = $(this).attr('data-id')
        // url
        url = $(this).attr('data-url')
        // cart id
        cart_id = $(this).attr('id')
        
        // ajax
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status == 'Login_required'){
                    swal(response.message,'','info').then(function(){
                        console.log('work');
                        window.location = '/login';
                    })
                } if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }if (response.status == 'Success'){
                    swal(response.message,'','success')
                    // load cart counter and quantity realtime
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    if (window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id)
                        checkEmptyCart()
                    }

                    // subtotal, tax and grand total
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total'],
                    )
                }
            }
        })
    })

    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e){
        e.preventDefault()
        
        // food id
        cart_id = $(this).attr('data-id')
        // url
        url = $(this).attr('data-url')
        
        // ajax
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }else{
                    swal(response.status,response.message,'success')
                    // load cart counter and quantity realtime
                    $('#cart_counter').html(response.cart_counter['cart_count'])

                    removeCartItem(0, cart_id)
                    checkEmptyCart()
                    // subtotal, tax and grand total
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total'],
                    )
                }
            }
        })
    })

    // delete the cart element if the qty is 0
    function removeCartItem(cartItemQty, cart_id){
        if (cartItemQty <=0){
            // remove the cart item realtime
            document.getElementById('cart-item-'+cart_id).remove()
        }
    }

    // check empty cart
    function checkEmptyCart(){
        let cart_counter = document.getElementById('cart_counter').innerHTML

        if (cart_counter == 0){
            document.getElementById('empty-cart').style.display = 'block'
        }
    }

    // apply cart amounts
    function applyCartAmounts(subtotal, tax, grand_total){
        if (window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)
        }
    }
})