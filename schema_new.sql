create table if not exists articles (
	id integer primary key autoincrement,
	url text not null,
	title text not null,
	read int default 0,
	interesting int default null,
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

create table if not exists settings (
	id INTEGER PRIMARY KEY CHECK (id = 0),
	name text,
	articles_to_show int default 10
);

insert into settings (id, name) VALUES (0, 'Anon');