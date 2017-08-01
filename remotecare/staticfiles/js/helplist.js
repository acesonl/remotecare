/* Helplist functions */

var Helplist = {
    openclose: function (event) {
		var doAdd = true;
        if ($(event).parent().hasClass("selected")) {
            doAdd = false;
        }
        $('#helplist ul li').removeClass("selected");

        $.Event(event).preventDefault();
        if(doAdd) 
            $(event).parent().addClass("selected");
        else 
            $(event).parent().removeClass("selected");


        $('.scrollbar_container').tinyscrollbar();	
    }
}
