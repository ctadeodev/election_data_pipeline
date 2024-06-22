{{ config(materialized='table') }}

with votes_with_voters as (
    select
        dv.state,
        dv.voter_id,
        v.vote_timestamp
    from {{ ref('fct_votes') }} v
    full join {{ ref('int_voters') }} dv on v.voter_id = dv.voter_id
)

select
    state,
    count(distinct case when vote_timestamp is not null then voter_id end) as voted,
    count(distinct case when vote_timestamp is null then voter_id end) as did_not_vote
from votes_with_voters
group by state
