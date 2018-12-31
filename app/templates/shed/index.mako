<%inherit file="app:templates/base.mako" />

<%block name="title">Engine Shed</%block>

<%block name="scripts">
	<script>
		$(function() {
//			$("#engines").tabs();
		});
	</script>
</%block>

<div class="row">
	<div class="col-sm-12 text-right">
		<button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#addEngineModal">Add Engine</button>
	</div>
</div>

<div class="row">
	<div class="col-sm-12">
		<div id="engines" class="form-horizontal">
			<ul class="nav nav-tabs">
% for e in engines:
				<li class="${'active' if e.id == id else ''}">
					<a data-toggle="tab" href="#tabs-${e.id}">${e.nickname}</a>
				</li>
% endfor
			</ul>
			<div class="tab-content panel panel-default">
% for e in engines:
				<div id="tabs-${e.id}" class="tab-pane ${'active' if e.id == id else ''} panel-body">
					<form action="/shed/save?id=${e.id}" method="POST"> 
						<div class="form-group text-right">
							<div class="col-sm-12">
% if e.addr != None:
								<a class="btn btn-primary" href="/cab/drive?id=${e.id}">Drive!</a>
% endif
								<input type="submit" class="btn btn-default" value="Save">
								<a class="btn btn-default" href="/shed/delete?id=${e.id}"
									data-toggle="modal" data-target="#confirmModal">
									Delete
								</a>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">Name</label>
							<div class="col-sm-9">
								<input type="text" class="form-control" name="nickname" value="${e.nickname}">
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">DCC Address</label>
							<div class="col-sm-9">
								<input type="text" class="form-control" name="addr" value="${e.addr if e.addr else ''}">
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">Max Speed</label>
							<div class="col-sm-9">
								<input type="number" class="form-control" name="maxSpeed" required min="1" max="28" value="${e.maxSpeed}">
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">Acceleration</label>
							<div class="col-sm-9">
								<input type="number" disabled class="form-control" min="1" max="10">
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">Braking</label>
							<div class="col-sm-9">
								<input type="number" disabled class="form-control" min="1" max="10">
							</div>
						</div>
					</form>
				</div>
% endfor
			</div>
		</div>
	</div>
</div>

<!-- Modal -->
<div class="modal fade" id="addEngineModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
	<div class="modal-dialog" role="document">
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
				<h4 class="modal-title" id="myModalLabel">Add Engine</h4>
			</div>
<form action="/shed/add" class="form-horizontal">
			<div class="modal-body">
				<div class="form-group">
					<label class="col-sm-3 control-label">Name</label>
					<div class="col-sm-9">
						<input type="text" name="nickname" class="form-control" value="">
					</div>
				</div>
				<div class="form-group">
					<label class="col-sm-3 control-label">DCC Address</label>
					<div class="col-sm-9">
						<input type="text" name="addr" class="form-control" value="">
					</div>
				</div>
				<div class="form-group">
					<label class="col-sm-3 control-label">Max Speed</label>
					<div class="col-sm-9">
						<input type="number" name="maxSpeed" class="form-control" required min="1" max="28" value="28">
					</div>
				</div>
				<div class="form-group">
					<label class="col-sm-3 control-label">Acceleration</label>
					<div class="col-sm-9">
						<input type="number" disabled class="form-control" min="1" max="10">
					</div>
				</div>
				<div class="form-group">
					<label class="col-sm-3 control-label">Braking</label>
					<div class="col-sm-9">
						<input type="number" disabled class="form-control" min="1" max="10">
					</div>
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
				<button type="save" class="btn btn-primary">Save</button>
			</div>
</form>
		</div>
	</div>
</div>
