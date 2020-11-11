// Add product to cart
$('[name="btn-add-prduct-cart"]').click(function(e){
    let parentElem = e.currentTarget    // this is the element that has the click listener
                        .parentElement; // this is parent of the element
    let productIdElem;
    let addCartUrlElem;

    for (let i = 0; i < parentElem.childNodes.length; i++) {
        if (parentElem.childNodes[i].name == "product-id") {
            productIdElem = parentElem.childNodes[i];
            break;
        }
    }

    let productId = parseInt(productIdElem.value);

    $.ajax({
        url: '/add_cart/',
        type: 'post',
        dataType: 'json',
        data: {
            productId: productId
        },
        success: function(result){
            document.getElementById("product-num-in-cart").innerHTML = result.cart.total.toString();
        },
        error: function(error){
            console.log(error);
        }
    });
});