<%inherit file="app:templates/base.mako" />

<%block name="title">Cab Control</%block>

<%block name="scripts">
	<script>
		$(function() {
			// Make progress bars work vertically (bit hacky, alas)
			$.widget("ui.progressbar", $.ui.progressbar, {
				"value": function(val) {
					this.options.value = val;
					var percent = 100 * val / this.options.max;
					$(this.valueDiv).css({
						// Something strange happens if I try to set margin-top as a %, so ...
						"margin-top": $(this.element).height() * (100 - percent) / 100 + "px",
						"height": percent + "%",
						"width": "100%",
					}).toggle(val != 0);
				},
				_setOptions: function(optMap) {
					if ("value" in optMap) {
						console.log("Sorry, you need to call progressbar('value', n) to set the value, cos intercepting _setOption() isn't working :-(");
					}
					this._super(optMap);
				},
			});

			$("#throttle").slider({
				orientation: "vertical",
				min: 0,
				max: 28,
				value: 0,
			});
			$("#speedo").progressbar({
				value: 0,
				max: 28,
			});
			setInterval(function() {
				$.post({
					url: "/cab/update?id=${addr}",
					data: {
						throttle: $("#throttle").slider("value"),
						direction: $("input[name=direction]:checked").val(),
					},
					success: function(status) {
						$("#speedo").progressbar("value", status.speed);
						$("#speed").val(status.speed);
					},
					dataType: "json",
				});
			}, 200);
		});
	</script>
	<style>
		#throttle, #speedo {
			height: 200px;
		}
		#throttle {
			width: 20%;
			margin-left: 40%;
		}
		#throttle .ui-slider-handle {
			width: 500%;
			left: -200%;
		}
	</style>
</%block>

<div class="row">
	<div class="col-sm-12">
		<p><a href="/shed/index">&lt; Back to engine shed</a>
	</div>
</div>

<div class="row">
	<div class="col-xs-6">
		<div id="speedo" class="form-group"></div>
		<div class="row form-group">
			<div class="col-sm-12">
				<input id = "speed" readonly class="form-control">
			</div>
		</div>
	</div>
	<div class="col-xs-6">
		<div id="throttle" class="form-group"></div>
		<div class="row form-group" style="display: none">
			<div class="col-sm-6">
				<button class="btn btn-default btn-block">Slower</button>
			</div>
			<div class="col-sm-6">
				<button class="btn btn-default btn-block">Faster</button>
			</div>
		</div>
		<div class="row form-group" data-toggle="buttons">
			<div class="col-sm-6">
				<label class="btn btn-default btn-block">
					<input type="radio" name="direction" value="-1" style="display: none" autocomplete="off">Backwards
				</label>
  			</div>
			<div class="col-sm-6">
				<label class="btn btn-default btn-block active">
					<input type="radio" name="direction" value="1" checked style="display: none" autocomplete="off">Forwards
				</label>
  			</div>
		</div>
	</div>
</div>
<div class="row">
	<div class="col-sm-12">
		<button class="btn btn-danger btn-block">Emergency Stop</button>
	</div>
</div>

