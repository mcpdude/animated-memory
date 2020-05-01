# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>
<h2><a href="/">Back to the big list</a></h2>
<h1>List of Articles</h1>

<ul id="articles">
% if articles:
  % for article in articles:
  <li>
    <span class="name"><a href="${article['url']}" target="_blank">${article['title']}</a> ${article['interesting']}</span>
    <span class="actions">
      [ <a href="${request.route_url('interesting', id=article['id'])}">interesting</a> ]
      [ <a href="${request.route_url('not_interesting', id=article['id'])}">not interesting</a> ]
    </span>
  </li>
  % endfor
% else:
  <li>You haven't rated any articles yet.</li>
% endif
  <li class="last">
    <a href="${request.route_url('new')}">Add a new source?</a>
  </li>
</ul>