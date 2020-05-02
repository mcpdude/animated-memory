create table if not exists articles (
	id integer primary key autoincrement,
	url text not null,
	title text not null,
	read int default 0,
	local_html_path text,
	interesting int default 0,
	visible int default 1,
	source_id int not null,
	added_timestamp text default (datetime('now')),
	inferred_interest real default 0.0,
	blurb text
);

create table if not exists sources (
	id integer primary key autoincrement,
	root_url text not null,
	name text not null,
	date_added text default (datetime('now'))
);

