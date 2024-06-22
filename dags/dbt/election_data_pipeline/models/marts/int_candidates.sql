{{ config(materialized='table') }}

select
    candidate_id,
    full_name,
    party,
    election_id
from {{ ref('stg_candidates') }}
