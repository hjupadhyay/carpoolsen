$(document).ready(function(){

	var jVal = {
		'gender' : function (){

			$('body').append('<div id="genderInfo" class="valid"></div>');

			var genderInfo = $('#genderInfo');
			var ele = $('#f');
			var pos = ele.offset();

			genderInfo.css({
				top: pos.top+1,
				left: pos.left+ele.outerWidth()+55
			});

			if($('input[name="gender"]:checked').length == 0) {
				jVal.errors = true;
					genderInfo.removeClass('correct').addClass('error').html('&larr; Please select your Gender!').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					genderInfo.removeClass('error').addClass('correct').html('&radic; Okay').hide();
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
				left: pos.left+ele.outerWidth()+45
			});
            
            var patt = /^[a-zA-Z0-9]+$/i;
            var pat = /^[a-zA-Z]+./i;
            
			var xmlhttp = new XMLHttpRequest();
			var data = new FormData();
			data.append("username",ele.val());
            data.append("search","username");
			xmlhttp.open("POST","/search/",true);
			xmlhttp.send(data);
			xmlhttp.onreadystatechange = function() {
                if(ele.val() == 0){
                    jVal.errors = true;
                        uname.removeClass('correct').addClass('error').html('&larr; Enter a username').show();
                        ele.removeClass('normal').addClass('wrong');
                } else {
                    if(!patt.test(ele.val())) {
                        jVal.errors = true;
                        uname.removeClass('correct').addClass('error').html('&larr; Only alpha-numeric username allowed').show();
                        ele.removeClass('normal').addClass('wrong');
                    } else {
                        if(!pat.test(ele.val())) {
                            jVal.errors = true;
                            uname.removeClass('correct').addClass('error').html('&larr; Start with alphabet').show();
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
				left: pos.left+ele.outerWidth()-270
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
				left: pos.left+ele.outerWidth()-280
			});
            
            var char = /^[a-zA-Z]+./i;
            var num = /^[0-9]+./i;
            var spech = /^!@#\$%\^\&*\(\)_;:'"/g;

			if(ele.val().length == 0) {
				jVal.errors = true;
					passwd.removeClass('correct').removeClass('medium').removeClass('weak').addClass('error').html('Enter a Password &rarr;').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
                if(char.test(ele.val()) && num.test(ele.val()) && spech.test(ele.val())) {
                    passwd.removeClass('error').removeClass('medium').removeClass('weak').addClass('correct').html('Strong &rarr;').show();
                    ele.removeClass('wrong').addClass('normal');
                } else{
                    if(char.test(ele.val()) && num.test(ele.val()) || char.test(ele.val()) && spech.test(ele.val()) || num.test(ele.val()) && spech.test(ele.val())) {
                        passwd.removeClass('error').removeClass('correct').removeClass('weak').addClass('medium').html('Medium &rarr;').show();
                        ele.removeClass('wrong').addClass('normal');
                    } else {
                        if(char.test(ele.val()) || num.test(ele.val()) || spech.test(ele.val())) {
                            passwd.removeClass('error').removeClass('medium').removeClass('correct').addClass('weak').html('Weak &rarr;').show();
                            ele.removeClass('wrong').addClass('normal');
                        } else {
                            jVal.errors = true;
                            passwd.removeClass('correct').removeClass('medium').removeClass('weak').addClass('error').html('Erroneous Password &rarr;').show();
                            ele.removeClass('normal').addClass('wrong');
			}
            }
            }
            }
			
			if(ele.val().length == 0){
                jVal.errors = true;
                conf_passwd.hide();
                ele.removeClass('normal').addClass('wrong');
            } else {
			if(ele.val() != ele2.val()) {
				jVal.errors = true;
					conf_passwd.removeClass('correct').addClass('error').html('&larr; Not matching').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					conf_passwd.removeClass('error').addClass('correct').html('&radic; Matches').show();
					ele.removeClass('wrong').addClass('normal');
			}
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

            if(ele2.val().length == 0){
                    jVal.errors = true;
                        conf_passwd.hide();
                        ele.removeClass('normal').addClass('wrong');
            } else {
			if(ele.val() != ele2.val()) {
				jVal.errors = true;
					conf_passwd.removeClass('correct').addClass('error').html('&larr; Not matching').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					conf_passwd.removeClass('error').addClass('correct').html('&radic; Matches').show();
					ele.removeClass('wrong').addClass('normal');
			}
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
            data.append("search","car_number");
            xmlhttp.open("POST","/search",true);
            xmlhttp.send(data);
            xmlhttp.onreadystatechange = function() {
			if(!patt.test(ele.val())) {
				jVal.errors = true;
					emailInfo.removeClass('correct').addClass('error').html('&larr; Wrong format').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
                if(xmlhttp.responseText=="1") {
                    jVal.errors = true;
                        emailInfo.removeClass('correct').addClass('error').html('&larr; already taken').show();
                        ele.removeClass('normal').addClass('wrong');
                } else{
					emailInfo.removeClass('error').addClass('correct').html('&radic; Alright!').show();
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
            
            var patt = /\D/i;

			if(ele.val().length < 10 || ele.val().length > 15 || patt.test(ele.val())) {
				jVal.errors = true;
					phoneInfo.removeClass('correct').addClass('error').html('&larr; Wrong Format').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					phoneInfo.hide();
					ele.removeClass('wrong').addClass('normal');
			}
		},

        'sendIt' : function (){
            if(!jVal.errors) {
                $('#signupform').submit();
            }
        }
	};
    
// ====================================================== //

    $('#signup').click(function (){
        var obj = $.browser.webkit ? $('body') : $('html');
        console.log("yoooo");
        obj.animate({ scrollTop: $('#gender').offset().top }, 750, function (){
            jVal.errors = false;
            jVal.gender();
            jVal.usern();
            jVal.firstn();
            jVal.passwd();
            jVal.conf_passwd();
            jVal.email();
            jVal.phone();
            jVal.sendIt();
        });
        return false;
    });

	// bind jVal.usern function to "User name" form field
	$('input[name="gender"]').change(jVal.gender);
	$('#username').change(jVal.usern);
	$('#first_name').change(jVal.firstn);
	$('#password').change(jVal.passwd);
	$('#confirmpassword').change(jVal.conf_passwd);
	$('#email').change(jVal.email);
	$('#phone').change(jVal.phone);

});