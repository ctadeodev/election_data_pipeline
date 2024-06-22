{{ config(materialized='table') }}

select
    voter_id,
    full_name,
    dob,
    gender,
    registration_date,
    state
from {{ ref('stg_voters') }}
