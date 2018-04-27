<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<!-- jQuery -->
		<script src="/static/jquery-3.2.1.min.js"></script>
		<!-- jQueryUI -->
		<link rel="stylesheet" href="/static/jquery-ui.min.css">
		<script src="/static/jquery-ui.min.js"></script>
		<!-- Bootstrap -->
		<link rel="stylesheet" href="/static/bootstrap.css">
		<script src="/static/bootstrap.js"></script>

		<title><%block name="title">Block title</%block></title>
		<style>
			.tab-content {
				border-top: 0;
				border-top-right-radius: 0;
				border-top-left-radius: 0;
			}
			h1, h2 {
				font-weight: bold;
			}
			.h1, .h2, .h3, h1, h2, h3 {
				margin-top: 0px;
			}
		</style>
		<%block name="head"></%block>
		<%block name="scripts"/>
	</head>
      	<body class="panel-body">
		<h2>${self.title()}</h2>
		${self.body()}

<!-- Modal -->
<div class="modal fade" id="confirmModal" tabindex="-1" role="dialog">
	<script>
		$(function() {
			// Whenever any link is clicked
			$("a").click(function(event) {
				// If it will open the confirmation modal...
				if ($(this).data("target") == "#confirmModal") {
					$(this).data("remote", false);
					// we shoud Not go to the page (yet)
					event.preventDefault();
				};
			});
			$("#confirmModal").on("show.bs.modal", function(event) {
				$(this).data("triggerElement", $(event.relatedTarget));
				var buttonText = $(event.relatedTarget).val() || $(event.relatedTarget).text() || "Confirm";
				$(this).find("button.confirm").text(buttonText);
				// TODO: Use the text on the trigger element as
				// the text on the confirm button
			});
			$("#confirmModal button.confirm").click(function(event) {
				$("#confirmModal").data("triggerElement").trigger("confirmed");
			});
			$("body").on("confirmed", "a", function() {
				// Link confirmed: follow it
				window.location = this.href;
			});
		});
	</script>
	<div class="modal-dialog" role="document">
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
				<h4 class="modal-title" id="myModalLabel">Confirm</h4>
			</div>
			<div class="modal-body">
				<p>Are you sure about that?</p>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
				<button type="button" class="btn btn-primary confirm">Confirm</button>
			</div>
		</div>
	</div>
</div>
	</body>
</html>

