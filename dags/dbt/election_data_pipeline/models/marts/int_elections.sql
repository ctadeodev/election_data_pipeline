{{ config(materialized='table') }}

select
    election_id,
    election_name,
    election_date
from {{ ref('stg_elections') }}
