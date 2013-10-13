quoteCache = {};

$(document).keyup(function(e){
	if (e.keyCode == 13) {
		$("form").submit();
	}
	var $quote = $(".quote"),
		$beforeContext = $quote.prevAll("[class|=context]"),
		$afterContext = $quote.nextAll("[class|=context]"),
		changed = false;

	if (e.keyCode == 38 && $beforeContext.length > 0) {
		e.preventDefault();
		var newContextId = $beforeContext.last().data("prev");
			newContextClass = $beforeContext.last().attr("class");

		for (var i = $beforeContext.length-1; i >= 1; i--) {
			$beforeContext.eq(i).attr("class", $beforeContext.eq(i-1).attr("class")); 
		}
		$beforeContext.first().removeClass("context-1").addClass("quote");

		for (var i = 0; i < $afterContext.length-1; i++) {
			$afterContext.eq(i).attr("class", $afterContext.eq(i+1).attr("class")); 
		}
		$afterContext.last().remove();
		changed = "prev";
	}
	else if (e.keyCode == 40 && $afterContext.length > 0) { 
		e.preventDefault();
		var newContextId = $afterContext.last().data("next");
			newContextClass = $afterContext.last().attr("class");

		for (var i = $afterContext.length-1; i >= 1; i--) {
			$afterContext.eq(i).attr("class", $afterContext.eq(i-1).attr("class")); 
		}
		$afterContext.first().removeClass("context-1").addClass("quote");

		for (var i = 0; i < $beforeContext.length-1; i++) {
			$beforeContext.eq(i).attr("class", $beforeContext.eq(i+1).attr("class")); 
		}
		$beforeContext.last().remove();
		changed = "next";
	}

	if (changed) {
		$quote.removeClass("quote");
		$quote.addClass("context-1");

		if (newContextId) {
			if (newContextId in quoteCache) {
				if (changed == "prev") {
					$(".quotes").prepend(quoteCache[newContextId]);
				} else {
					$(".quotes").append(quoteCache[newContextId]);
				}
				return;
			}
			$.get('/'+newContextId+'?response=raw', function(data, textStatus, jqXHR) {
				var $el = $(data).attr("class", newContextClass);
				quoteCache[newContextId] = $el;
				if (changed == "prev") {
					$(".quotes").prepend($el);
				} else {
					$(".quotes").append($el);
				}
			});
		}
	}
});
