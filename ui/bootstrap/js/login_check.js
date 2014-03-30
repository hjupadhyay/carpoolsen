 
$(document).ready(function(){

    var jVal = {
        'loginname' : functioon(){
            
            $('body').append('<div id="loginname" class="valid"></div>');
            
            var loginname = $('#loginname');
            var ele = $('#username');
        },
        
        'passwd' : function(){
            
            $('body').append('<div id="passwd" class="valid"></div>');
            
            var passwd = $('#passwd');
            var ele = $("#password");
        },
        
        'loginsend' : function(){
            
            var loginname = $('#loginname');
            var ele = $('#username');
            var passwd = $('#passwd');
            var ele2 = $("#password");
            
            if(!jVal.errors) {
                $('#loginform').submit();
            }
        },
        
    };
    
    $('#login').click(function (){
        var obj = $.browser.webkit ? $('body') : $('html');
        obj.animate({ scrollTop: $('#username').offset().top }, 750, function (){
            jVal.errors = false;
            jVal.loginname();
            jVal.passwd();
            jVal.loginsend();
        });
        return false;
    });
    $('#username').change(jVal.loginname);
    $('#password').change(jVal.passwd);
    
});