use role accountadmin;
create role if not exists dbt_role;
grant role dbt_role to user mjmendez;

create warehouse if not exists election_wh with warehouse_size='x-small';
create database if not exists election_db;
grant usage on warehouse election_wh to role dbt_role;
grant all on database election_db to role dbt_role;

use role dbt_role;
create schema if not exists election_db.election_schema;