drop table if exists temperatures;
create table temperatures (
  id integer primary key autoincrement,
  date timestamp null,
  value float not null
);
