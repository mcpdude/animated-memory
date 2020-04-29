# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>List of Articles</h1>

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
    <a href="${request.route_url('new')}">Add a new source</a>
  </li>
</ul>