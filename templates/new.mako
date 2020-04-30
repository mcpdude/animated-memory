# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>
<h2><a href="/">Back to the big list</a></h2>
<h1>Add a new source</h1>

<form action="${request.route_url('new')}" method="post">
  <input type="text" name="name" placeholder="Name of the source">
  <input type="text" name="url" placeholder="URL">
  <input type="submit" name="add" value="ADD" class="button">
</form>

<h2>Current Sources</h2>
<ul id="sources">
% if sources:
  % for source in sources:
  <li>
    <span class="name"><a href="${source['url']}">${source['name']}</a></span>
    <span class="actions">
      [ <a href="${request.route_url('delete_source', id=source['id'])}">delete?</a> ]
    </span>
  </li>
  % endfor
% else:
  <li>There are no sources. Maybe add a source?</li>
% endif
</ul>