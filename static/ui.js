function prepareUI()
{
		// Prepare UI

//		$(".usertable tr.userrow").hover(function() {
//				$(this).find("span").animate({opacity: "show"}, 0);
//		}, function() {
//				$(this).find("span").animate({opacity: "hide"}, 0);
//		});

		$(".dropdown").hover(function() {
				$(this).find("span").animate({opacity: "show"}, 200);
		}, function() {
				$(this).find("span").animate({opacity: "hide"}, 200);
		});
		
//		$(".usertable tr:odd").addClass("odd");
}

$(document).ready(prepareUI);
