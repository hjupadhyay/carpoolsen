$(document).ready(function(){

	var jVal = {
		'gender' : function (){

			$('body').append('<div id="genderInfo" class="info"></div>');

			var genderInfo = $('#genderInfo');
			var ele = $('#f');
			var pos = ele.offset();

			genderInfo.css({
				top: pos.top-10,
				left: pos.left+ele.outerWidth()+60
			});

			if($('input[name="gender"]:checked').length == 0) {
				jVal.errors = true;
// 					genderInfo.removeClass('correct').addClass('error').html('&larr; Are you a man or a woman?').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
// 					genderInfo.removeClass('error').addClass('correct').html('&radic; Okay').show();
					ele.removeClass('wrong').addClass('normal');
			}
		},
	  
		'usern' : function() {

			$('body').append('<div id="uname" class="valid"></div>');

			var uname = $('#uname');
			var ele = $('#username');
			var pos = ele.offset();

			uname.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});
			var xmlhttp = new XMLHttpRequest();
			var data = new FormData();
			data.append("username",ele.val());
			xmlhttp.open("POST","/search_username/",true);
			xmlhttp.send(data);
			xmlhttp.onreadystatechange = function() {
                if(ele.val() == 0){
                    jVal.errors = true;
                        uname.removeClass('correct').addClass('error').html('&larr; Enter a username').show();
                        ele.removeClass('normal').addClass('wrong');
                } else {
                if(xmlhttp.responseText=="1") {
                    jVal.errors = true;
                        uname.removeClass('correct').addClass('error').html('&larr; already taken').show();
                        ele.removeClass('normal').addClass('wrong');
                } else {
                        uname.removeClass('error').addClass('correct').html('&radic; available').show();
                        ele.removeClass('wrong').addClass('normal');
                }
                }
			}
		},
		
		'firstn' : function() {

			$('body').append('<div id="fname" class="valid"></div>');

			var fname = $('#fname');
			var ele = $('#first_name');
			var pos = ele.offset();

			fname.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()-275
			});

			if(ele.val().length == 0) {
				jVal.errors = true;
					fname.removeClass('correct').addClass('error').html('Input Something &rarr;').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					fname.hide();
					ele.removeClass('wrong').addClass('normal');
			}
		},
		
		'passwd' : function() {

			$('body').append('<div id="passwd" class="valid"></div>');
			$('body').append('<div id="conf_passwd" class="valid"></div>');

			var passwd = $('#passwd');
			var conf_passwd = $('#conf_passwd');
			var ele = $('#password');
			var ele2 = $('#confirmpassword');
			var pos = ele.offset();

			passwd.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()-275
			});

			if(ele.val().length == 0) {
				jVal.errors = true;
					passwd.removeClass('correct').addClass('error').html('&larr; Enter a Password').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					passwd.hide();
					ele.removeClass('wrong').addClass('normal');
			}
			
			if(ele.val() != ele2.val()) {
				jVal.errors = true;
					conf_passwd.removeClass('correct').addClass('error').html('&larr; Not matching').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					conf_passwd.removeClass('error').addClass('correct').html('&radic; Matches').show();
					ele.removeClass('wrong').addClass('normal');
			}
		},
		
		'conf_passwd' : function() {

			$('body').append('<div id="conf_passwd" class="valid"></div>');

			var conf_passwd = $('#conf_passwd');
			var ele = $('#confirmpassword');
			var ele2 = $('#password');
			var pos = ele.offset();

			conf_passwd.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+10
			});

			if(ele.val() != ele2.val()) {
				jVal.errors = true;
					conf_passwd.removeClass('correct').addClass('error').html('&larr; Not matching').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					conf_passwd.removeClass('error').addClass('correct').html('&radic; Matches').show();
					ele.removeClass('wrong').addClass('normal');
			}
		},
		
		'email' : function() {

			$('body').append('<div id="emailInfo" class="info"></div>');

			var emailInfo = $('#emailInfo');
			var ele = $('#email');
			var pos = ele.offset();

			emailInfo.css({
				top: 3,
				left: 2
			});

			var patt = /^.+@.+[.].{2,}$/i;

			if(!patt.test(ele.val())) {
				jVal.errors = true;
// 					emailInfo.removeClass('correct').addClass('error').html('&larr;').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
// 					emailInfo.removeClass('error').addClass('correct').html('&radic; you so pro!').show();
					ele.removeClass('wrong').addClass('normal');
			}
		},
		
		'car_no' : function() {

			$('body').append('<div id="car_noInfo" class="valid"></div>');

			var car_noInfo = $('#car_noInfo');
			var ele = $('#car_number');
			var pos = ele.offset();

			car_noInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});
            var xmlhttp = new XMLHttpRequest();
            var data = new FormData();
            data.append("car_number",ele.val());
            xmlhttp.open("POST","/search_car_number/",true);
            xmlhttp.send(data);
            xmlhttp.onreadystatechange = function() {
                if(xmlhttp.responseText=="1") {
                    jVal.errors = true;
                        car_noInfo.removeClass('correct').addClass('error').html('&larr; already taken').show();
                        ele.removeClass('normal').addClass('wrong');
                } else {
                        car_noInfo.removeClass('error').addClass('correct').html('&radic; available').show();
                        ele.removeClass('wrong').addClass('normal');
                }
            }
		},
		
		'phone' : function() {

			$('body').append('<div id="phoneInfo" class="valid"></div>');

			var phoneInfo = $('#phoneInfo');
			var ele = $('#phone');
			var pos = ele.offset();

			phoneInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+40
			});

			if(ele.val().length < 10 || ele.val().length > 15) {
				jVal.errors = true;
					phoneInfo.removeClass('correct').addClass('error').html('&larr; Wrong Format').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					phoneInfo.hide();
					ele.removeClass('wrong').addClass('normal');
			}
		}
	};

	// bind jVal.usern function to "User name" form field
	$('input[name="gender"]').change(jVal.gender);
	$('#username').change(jVal.usern);
	$('#first_name').change(jVal.firstn);
	$('#password').change(jVal.passwd);
	$('#confirmpassword').change(jVal.conf_passwd);
	$('#email').change(jVal.email);
	$('#car_number').change(jVal.car_no);
	$('#phone').change(jVal.phone);

});