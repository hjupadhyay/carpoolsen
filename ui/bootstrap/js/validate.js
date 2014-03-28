$(document).ready(function(){

	var jVal = {
		'usern' : function() {

			$('body').append('<div id="uname" class="valid"></div>');

			var uname = $('#uname');
			var ele = $('#username');
			var pos = ele.offset();

			uname.css({
				top: pos.top-3,
				left: pos.left+ele.width()+15
			});

			if(ele.val().length < 6) {
				jVal.errors = true;
					uname.removeClass('correct').addClass('error').html('&larr; at least 6 characters').show();
					ele.removeClass('normal').addClass('wrong');
			} else {
					uname.removeClass('error').addClass('correct').html('&radic;').show();
					ele.removeClass('wrong').addClass('normal');
			}
		}
	};

	// bind jVal.usern function to "User name" form field
	$('#username').change(jVal.usern);

});