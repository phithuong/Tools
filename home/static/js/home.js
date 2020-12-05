// Add product to cart
$('[name="btn-add-prduct-cart"]').click(function (e) {
    let targetClassName = e.currentTarget.className;
    if (targetClassName === 'zmdi zmdi-shopping-cart-plus') {
        let styleOrderButton = e.target.style;
        let stylePlusMinusButton = e.target.nextElementSibling.style;

        // display add/subtract button product from cart
        styleOrderButton.display = "none";
        stylePlusMinusButton.display = "block";

        // hide add/subtract button product from cart
        setTimeout(function () {
            styleOrderButton.display = "block";
            stylePlusMinusButton.display = "none";
        }, 2000);
    }
});

$('.fa-plus').click(function (e) {
    let targetClassName = e.currentTarget.className;
    let parentElem;
    let orderValueElem;
    // zmdi zmdi-shopping-cart-plus
    // fas fa-plus
    if (targetClassName === 'zmdi zmdi-shopping-cart-plus') {
        parentElem = e.currentTarget    // this is the element that has the click listener
            .parentElement; // this is parent of the element
    }
    if (targetClassName === 'fas fa-plus') {
        parentElem = e.currentTarget.parentElement.parentElement;
        orderValueElem = e.target.previousElementSibling;
    }

    let productIdElem;

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
        success: function (result) {
            document.getElementById("product-num-in-cart").innerHTML = result.cart.total.toString();
            if (orderValueElem) {
                let orderValue = orderValueElem.innerHTML;
                orderValueElem.innerHTML = String(Number(orderValue) + 1);
            }
        },
        error: function (error) {
            console.log(error); // this comment for delete
        }
    });
});

$('.fa-minus').click(function (e) {
    console.log(e);
    // let targetClassName = e.currentTarget.className;
    grantParentElem = e.currentTarget.parentElement.parentElement;

    let productIdElem;

    for (let i = 0; i < grantParentElem.childNodes.length; i++) {
        if (grantParentElem.childNodes[i].name == "product-id") {
            productIdElem = grantParentElem.childNodes[i];
            break;
        }
    }

    let productId = parseInt(productIdElem.value);
    let orderValueElem = e.currentTarget.nextElementSibling;
    let orderValue = orderValueElem.innerHTML;
    $.ajax({
        url: '/remove_cart/',
        type: 'post',
        dataType: 'json',
        data: {
            productId: productId,
            isSubtract: true
        },
        success: function (result) {
            document.getElementById("product-num-in-cart").innerHTML = result.cart.total.toString();
            if (Number(orderValue) > 1) {
                orderValueElem.innerHTML = String(Number(orderValue) - 1);
            }
        },
        error: function (error) {
            console.log(error); // this comment for delete
        }
    });
});

// $('[name="btn-add-prduct-cart"], .fa-plus').click(function(e){
//     let parentElem = e.currentTarget    // this is the element that has the click listener
//                         .parentElement; // this is parent of the element
//     let productIdElem;
//     let addCartUrlElem; //this comment for delete

//     for (let i = 0; i < parentElem.childNodes.length; i++) {
//         if (parentElem.childNodes[i].name == "product-id") {
//             productIdElem = parentElem.childNodes[i];
//             break;
//         }
//     }
//     let productId = parseInt(productIdElem.value);

//     $.ajax({
//         url: '/add_cart/',
//         type: 'post',
//         dataType: 'json',
//         data: {
//             productId: productId
//         },
//         success: function(result){
//             document.getElementById("product-num-in-cart").innerHTML = result.cart.total.toString();
//         },
//         error: function(error){
//             console.log(error); // this comment for delete
//         }
//     });
// });

function search(textSearch) {
    let pathSearch = `/search/${textSearch}`;
    window.location.href = pathSearch;
}

$('#btn-search').click(
    () => {
        let textSearch = document.getElementById('text-search').value;
        search(textSearch);
    }
)
