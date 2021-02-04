var q = $('body');



$(document).ready(function(){
	q.queue(function(next){
		$('#hidden-div').css({animation: "ease-in 900ms grow-circle"}, next);
		$('#hidden-div').css('animation-fill-mode', 'forwards');
	});
    //$("#hidden-div").css({animation: "ease-in 500ms grow-circle"});
    //$('body').css("background", "linear-gradient(76.49deg, #00A99D 20.31%, #1DDDCF 93.34%)").delay();
    //$("#hidden-div").hide();
  //  return false;
});



$(document).ready(function(){
	var p = $('body')
	setTimeout(function (){
		p.css("background", "linear-gradient(76.49deg, #00A99D 20.31%, #1DDDCF 93.34%)");
		}, 850);
    });



/*
$(document).ready(function() {
    $('#hidden-div').each(function() {
        var h = $(this).height();
        $(this).height(h).addClass('noHeight').toggleClass('noHeight');
    });
});*/