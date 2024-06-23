{{ config(materialized='table') }}

with party_results_per_state as (
    SELECT
        state,
        party AS winning_party
    FROM (
        SELECT
            voter_state as state,
            candidate_party as party,
            votes,
            RANK() OVER (PARTITION BY state ORDER BY votes DESC) AS vote_rank
        FROM {{ ref('election_results') }}
    ) ranked_votes
    WHERE vote_rank = 1
    GROUP BY state, party
    ORDER BY state
)

select 
    r.state,
    r.winning_party,
    dc.candidate_id as winning_party_id
from party_results_per_state r
left join {{ ref('int_candidates') }} dc
on r.winning_party = dc.party