<h2>Alerts for {{email}}</h2>

<hr class='soften'>

<table class="table table-bordered table-striped">
<thead>
  <tr>
    <th style="width: 90%">term</th>
    <th></th>
  </tr>
</thead>
<tbody>
%for k, v in terms.iteritems():
  <tr>
    <td>{{k}}</td>
    <td><form method="post" action="http://localhost:8080/remove"><input type="hidden" name="remove_id" value="{{v['id']}}"><button type="Submit" class='btn btn-danger'><i class="icon-trash icon-white"></i>Delete</botton></form></td>
  </tr>
%end
</tbody>
</table>

{{!new_form}}

%rebase layout