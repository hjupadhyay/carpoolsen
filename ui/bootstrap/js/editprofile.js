$(document).ready(function(){

	var jVal = {
		
		'firstn' : function() {

			$('body').append('<div id="fname" class="valid"></div>');

			var fname = $('#fname');
			var ele = $('#first_name');
			var pos = ele.offset();

			fname.css({
				top: pos.top-2,
				left: pos.left+ele.outerWidth()+5
			});

			if(ele.val().length == 0) {
				jVal.errors = true;
				fname.removeClass('correct').addClass('error').html('&larr; Input Something').show();
				ele.removeClass('editchange').addClass('wrong');
			} else {
				fname.hide();
				ele.removeClass('wrong').addClass('editchange');
			}
			
			
		},
		
		'lastn' : function() {

			$('body').append('<div id="lname" class="valid"></div>');

			var lname = $('#lname');
			var ele = $('#last_name');
			var pos = ele.offset();

			lname.css({
				top: pos.top-2,
				left: pos.left+ele.outerWidth()+5
			});

			if(ele.val().length == 0) {
				jVal.errors = true;
				lname.removeClass('correct').addClass('error').html('&larr; Input Something').show();
				ele.removeClass('editchange').addClass('wrong');
			} else {
				lname.hide();
				ele.removeClass('wrong').addClass('editchange');
			}
			
			
		},
		
		'email' : function() {

			$('body').append('<div id="emailInfo" class="valid"></div>');

			var emailInfo = $('#emailInfo');
			var ele = $('#email');
			var pos = ele.offset();

			emailInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});

			var patt = /^.+@.+[.].{2,}$/i;
            var xmlhttp = new XMLHttpRequest();
            var data = new FormData();
            data.append("car_number",ele.val());
            data.append("search","email");
            xmlhttp.open("POST","/search_element/",true);
            xmlhttp.send(data);
            xmlhttp.onreadystatechange = function() {
			if(!patt.test(ele.val())) {
				jVal.errors = true;
					emailInfo.removeClass('correct').addClass('error').html('&larr; Wrong format').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
                if(xmlhttp.responseText=="1") {
                    jVal.errors = true;
                        emailInfo.removeClass('correct').addClass('error').html('&larr; already registered').show();
                        ele.removeClass('normal').addClass('wrong');
                } else{
					emailInfo.removeClass('error').addClass('correct').html('&radic; Alright!').hide();
					ele.removeClass('wrong').addClass('editchange');
			}
            }
            }
		},
		
		'phone' : function() {

			$('body').append('<div id="phoneInfo" class="valid"></div>');

			var phoneInfo = $('#phoneInfo');
			var ele = $('#phone_no');
			var pos = ele.offset();

			phoneInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});
            
            var patt = /\D/i;
            
            var xmlhttp = new XMLHttpRequest();
            var data = new FormData();
            data.append("phone",ele.val());
            data.append("search","phone");
            xmlhttp.open("POST","/search_element/",true);
            xmlhttp.send(data);
            xmlhttp.onreadystatechange = function() {
                if(ele.val().length != 10 || patt.test(ele.val())) {
                    jVal.errors = true;
					phoneInfo.removeClass('correct').addClass('error').html('&larr; Enter 10-digit Phone Number').show();
					ele.removeClass('normal').addClass('wrong');
                } else {
                    if(xmlhttp.responseText=="1") {
                        jVal.errors = true;
                        phoneInfo.removeClass('correct').addClass('error').html('&larr; already registered').show();
                        ele.removeClass('editchange').addClass('wrong');
                    } else {
                        phoneInfo.hide();
                        ele.removeClass('wrong').addClass('editchange');
                    }
                }
            }
		},
		
		'vehicle' : function() {

			$('body').append('<div id="vehicleInfo" class="valid"></div>');

			var vehicleInfo = $('#vehicleInfo');
			var ele = $('#vehicle_no');
			var pos = ele.offset();

			vehicleInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});
                        
            var xmlhttp = new XMLHttpRequest();
            var data = new FormData();
            data.append("vehicle",ele.val());
            data.append("search","vehicle");
            xmlhttp.open("POST","/search_element/",true);
            xmlhttp.send(data);
            xmlhttp.onreadystatechange = function() {
             
                    
                    if(xmlhttp.responseText=="1") {
                        jVal.errors = true;
                        vehicleInfo.removeClass('correct').addClass('error').html('&larr; already registered').show();
                        ele.removeClass('editchange').addClass('wrong');
                    } else {
                        vehicleInfo.hide();
                        ele.removeClass('wrong').addClass('editchange');
                    }
                }
            
		},

        'done' : function (){
            if(!jVal.errors) {
                $('#profileform').submit();
            }
        },
	};
    
// ====================================================== //

    $('#editprofile').click(function (){
        var obj = $.browser.webkit ? $('body') : $('html');
        obj.animate({ scrollTop: $('#profileform').offset().top }, 750, function (){
            jVal.errors = false;
            jVal.firstn();
	    jVal.lastn();
            jVal.email();
            jVal.phone();
	    jVal.vehicle();
            jVal.done();
        });
        return false;
    });
    
	$('#first_name').change(jVal.firstn);
	$('#last_name').change(jVal.lastn);
	$('#email').change(jVal.email);
	$('#phone_no').change(jVal.phone);
	$('#vehicle_no').change(jVal.vehicle);

});