drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null,
  postDate date not null
);

-- drop table if exists users;
-- create table users (
--   id integer primary key autoincrement,
--   user text not null,
--   pass text not null,
--   bio text not null
-- );