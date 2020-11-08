


// Add product to cart
$('#btn-add-prduct-cart').click(function(){
    $.ajax({
        url: '/add_cart',
        type: 'post',
        dataType: 'json',
        success: function(result){
            let productNumObj = $('#product-num-in-cart');
            let productNumInCart = parseInt(productNumObj.innerHtml);
            productNumObj.innerHtml = (productNumInCart + 1).toString();
        }
    });
});