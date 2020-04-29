create table if not exists articles (
	id integer primary key autoincrement,
	url text not null,
	title text not null,
	read int default 0,
	local_html_path text,
	interesting int default 0
);

create table if not exists sources (
	id integer primary key autoincrement,
	root_url text not null,
	name text not null
);

insert into sources (root_url, name) values ('https://pjmedia.com/instapundit/', 'instapundit')
