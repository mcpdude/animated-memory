# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>
<h2><a href="/">Back to the list</a></h2>
<h1>Settings</h1>

<form action="${request.route_url('change_settings')}" method="get">
	Name: ${settings[0]['name']}
	<input type="text" name="name" placeholder="Your Name Here">
	<input type="submit" name="field" value="Change Name" class="button">
</form>

<form action="${request.route_url('change_settings')}" method="get">
	Articles to show: ${settings[0]['articles_to_show']}
	<input type="text" name="articles_to_show" placeholder="Articles to Show">
	<input type="submit" name="field" value="Articles to Show" class="button">
</form>