##
## DCC - Digital Command Control command station
## Copyright (C) 2018 Simon Howkins
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
## Source for this program is published at https://github.com/simonhowkins/dcc
##
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
				max: ${maxSpeed},
				value: 0,
				slide: function(event, ui) {
					doUpdate({
						throttle: ui.value,
					});
				}
			});
			$("#speedo").progressbar({
				value: 0,
				max: ${maxSpeed},
			});
			$("input[name=direction]").change(function() {
				doUpdate({
					direction: this.value,
				});
			});
			var doUpdate = function(data) {
				$.post({
					url: "/cab/update?id=${addr}",
					data: data,
					success: function(status) {
						$("#speedo").progressbar("value", status.speed);
						$("#speed").val(status.speed);
						$("#throttle").slider("value", status.throttle);
						$("input[name=direction]").filter(function() {
							return this.value == status.direction;
						}).closest(".btn").button("toggle");
						$("input[name=direction]").closest(".btn").toggleClass("disabled", status.throttle !== 0 || status.speed !== 0);
					},
					dataType: "json",
				});
			};
			setInterval(function() {
				doUpdate({});
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

