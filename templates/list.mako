# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>List of Articles</h1>
<form action="${request.route_url('refresh')}" method="get">
  <input type="submit" name="add" value="Refresh articles" class="button">
</form>

<ul id="articles">
% if articles:
  % for article in articles:
  <li>
    <span class="name"><a href="${article['url']}" target="_blank">${article['title']}</a></span>
    <span class="actions">
      [ <a href="${request.route_url('interesting', id=article['id'])}">interesting</a> ]
      [ <a href="${request.route_url('not_interesting', id=article['id'])}">not interesting</a> ]
    </span>
  </li>
  % endfor
% else:
  <li>There are no new articles. Maybe add a source?</li>
% endif
  <li class="last">
    <a href="${request.route_url('new')}">Add/Delete a source</a>
  </li>

  <h3><a href="${request.route_url('read')}">Want to see the articles you've read before?</a></h3>
  <h3><a href="${request.route_url('settings')}">Settings</a></h3>
</ul>