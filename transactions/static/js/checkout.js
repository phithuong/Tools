$(".numeric").keydown(function(e){
    console.log(e);
});

function keyAbc(){
    $(".tele-phone").keydown(function (e) {
        console.log(e);
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
    $(".tele-phone").keyup(function(e) {  
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
            result = "(" + res + ") ";
            res = digits.substring(3);
        	result = result + res;
        	
            if(digits.length > 6){
                res = digits.substring(0, 3);
                result = "(" + res + ") ";
            	res = digits.substring(3,6);
            	result = result + res + "-";
            	res = digits.substring(6);
            	result = result + res;
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
keyAbc();

var radiosPayments = document.getElementsByName('choice-payments');
var bankInfo = document.querySelector('.bank-infor');

for(i=0; i<radiosPayments.length; i++ ) {
    radiosPayments[i].onclick = function(e) {
        if(e.target.defaultValue === "bank-tranfer"){
            bankInfo.style.display = "block";
        }else{
            bankInfo.style.display = "none";
        }
        if(e.ctrlKey) {
            this.checked = false;
        }
    }
}
var radiosShipTypes = document.getElementsByName('choice-ship');
for(i=0; i<radiosShipTypes.length; i++ ) {
    radiosShipTypes[i].onclick = function(e) {
        if(e.ctrlKey) {
            this.checked = false;
        }
    }
}