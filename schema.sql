
drop table if exists tweets;
create table tweets (
  id integer primary key autoincrement,
  username text not null,
  created_on DateTime not null,
  tweet text not null
);
