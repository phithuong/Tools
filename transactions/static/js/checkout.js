$(".fa-minus").click(function(e){
    let number = e.target.nextSibling.innerHTML;
    if (Number(number) > 1){
        e.target.nextSibling.innerHTML = String(Number(number) - 1);
    }
});
$(".fa-plus").click(function(e){
    // let number = document.getElementById("product-numbers").innerHTML;
    let number = e.target.previousSibling.innerHTML;
    e.target.previousSibling.innerHTML = String(Number(number) + 1);
});
$(".fa-trash-alt").click(function(e){
    let tableRow = e.target.parentElement.parentElement;
    tableRow.remove();
});
function checkPhoneNumber(){
    $("#tele-phone, #zipcode").keydown(function (e) {
        // Allow: backspace, delete, tab, escape, enter
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110]) !== -1 ||
             // Allow: Ctrl+A, Command+A
            (e.keyCode === 65 && (e.ctrlKey === true || e.metaKey === true)) || 
             // Allow: home, end, left, right, down, up
            (e.keyCode >= 35 && e.keyCode <= 40)) {
                 // let it happen, don't do anything
                 return;
        }
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
    $("#tele-phone, #zipcode").keyup(function(e) {  
    	var numericvalue = $(this); 
    	var position = getCursorPosition(numericvalue);
        if (// Allow: Ctrl+A, Command+A
            (e.keyCode === 65 && (e.ctrlKey === true || e.metaKey === true)) || 
             // Allow: home, end, left, right, down, up
            (e.keyCode >= 35 && e.keyCode <= 40)) {
                 // let it happen, don't do anything
                 return;
        }
	    var inputval = numericvalue.val();
	    digits = inputval.replace(/\D/g,'');
        
        if(digits.length > 2){
            res = digits.substring(0, 3);
            // result = "(" + res + ") ";
            result = res + "-";
            res = digits.substring(3);
        	result = result + res;
        	if($(this)[0].id === "tele-phone"){
                if(digits.length > 6){
                    res = digits.substring(0, 3);
                    result = res + "-";
                    res = digits.substring(3,6);
                    result = result + res + "-";
                    res = digits.substring(6);
                    result = result + res;
                }
            }
            numericvalue.val(result);
            result ="";
        }else{
        	numericvalue.val(digits);
        }
     	// Allow: backspace, delete, tab, escape, enter
    	if($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110]) !== -1){
    		setSelectionRange(numericvalue[0], position, position);
        }
    });
}
//Set cursor position
function setSelectionRange(input, selectionStart, selectionEnd) {
	  if (input.setSelectionRange) {
	    input.focus();
	    input.setSelectionRange(selectionStart, selectionEnd);
	  } else if (input.createTextRange) {
	    var range = input.createTextRange();
	    range.collapse(true);
	    range.moveEnd('character', selectionEnd);
	    range.moveStart('character', selectionStart);
	    range.select();
	  }
}

// Get cursor position
function getCursorPosition (numericvalue) {
        var pos = 0;
        var el = numericvalue.get(0);
        // IE Support
        if (document.selection) {
            el.focus();
            var Sel = document.selection.createRange();
            var SelLength = document.selection.createRange().text.length;
            Sel.moveStart('character', -el.value.length);
            pos = Sel.text.length - SelLength;
        }
        // Firefox support
        else if (el.selectionStart || el.selectionStart == '0')
            pos = el.selectionStart;
        return pos;
}
checkPhoneNumber();
var radiosPayments = document.getElementsByName('choice-payments');
var paymentsMethod = document.getElementsByClassName('payments-method');
var templateBankInfo = document.getElementById('bank-infor');
var templateDaibikiFee = document.getElementById('daibiki-bill');
var rItems = document.getElementsByClassName('row-item');

for(i=0; i<radiosPayments.length; i++ ) {
    radiosPayments[i].onclick = function(e) {
        if(e.target.defaultValue === "bank-tranfer"){
            var clone = templateBankInfo.content.cloneNode(true);
            if(!$('.bank-infor-wrapper').length){
                $(paymentsMethod).append(clone);
            }
        }else{
            if($('.bank-infor-wrapper')){
                $('.bank-infor-wrapper').remove();
            }
        }
        if(e.target.defaultValue === "daibiki"){
            var clone = templateDaibikiFee.content.cloneNode(true);
            if(!$('.row-daibiki-fee').length){
                $(rItems[rItems.length - 1]).after(clone);
            }
        }else{
            if($('.row-daibiki-fee')){
                $('.row-daibiki-fee').remove();
            }
        }
        if(e.ctrlKey) {
            this.checked = false;
        }
    }
}
var radiosShipTypes = document.getElementsByName('choice-ship');
for(i=0; i<radiosShipTypes.length; i++ ) {
    radiosShipTypes[i].onclick = function(e) {
        var templateDaibikiFee = document.getElementById('ship-bill');
        var rItems = document.getElementsByClassName('row-item');
        if(e.target.defaultValue === "type-ship-ice"){
            var clone = templateDaibikiFee.content.cloneNode(true);
            if(!$('.row-ship-fee').length){
                $(rItems[rItems.length - 1]).after(clone);
            }
        }else{
            if($('.row-ship-fee')){
                $('.row-ship-fee').remove();
            }
        }
        if(e.ctrlKey) {
            this.checked = false;
        }
    }
}


function zipCodeAutoGenerate(){
    $("#zipcode").change(function() {
        if($(this).val().length >= 7){
            // console.log($(this).val().replace('-',''));
            $.ajax({
                url: 'http://zipcloud.ibsnet.co.jp/api/search?zipcode=' + $(this).val().replace('-',''),
                dataType : 'jsonp',
            }).done(function(data) {
                if (data.results) {
                   setAddress(data.results[0]);
                } else {
                    alert('Chúng tôi không tìm thấy địa chỉ ứng với mã bưu điện của bạn.');
                    $('#address').val("");
                    $('#address').prop("disabled", true);
                }
            }).fail(function(data) {
                alert('Kết nối thất bại. Hãy liên lạc với quản trị viên.');
            });
            function setAddress(data) {
                $('#address').val(data.address1 + data.address2 + data.address3);
                $('#address').prop("disabled", false);
            }
        }
    });
}
zipCodeAutoGenerate();
