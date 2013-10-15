$(function() {
	$(".delete-quote").click(function(e){
		var $this = $(this);
		e.preventDefault();
		$.post(
			$this.attr("href"),
			function(data) {
				$this.parents("tr").first().fadeOut('fast');
			}
		);
	});

	$("body").on("click", ".editable", function(e) {
		$(".editing button").each(submitEdit);
		var $this = $(this),
			text = $this.text();

		$this.removeClass("editable").addClass("editing");
		$this.html('<button class="edit-submit" value="save">Save</button><input name="text" value="'+text+'"/>');
	});

	function submitEdit(e) {
		var $cell = $(this).parents("td").first(),
			text = $(this).siblings("input").first().val();
		$.post(
			'/quote_edit/'+$cell.data('id'),
			{'text': text},
			function(data) {
				$cell.html(text);
			}
		);
		$cell.removeClass("editing").addClass("editable");
	}

	$("body").on("click", ".edit-submit", submitEdit);
});