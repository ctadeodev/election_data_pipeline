{{ config(materialized='table') }}

select
    voter_state,
    election_name,
    candidate_name,
    candidate_party,
    count(vote_id) as votes
from {{ ref('fct_votes') }}
group by voter_state, election_name, candidate_name, candidate_party
