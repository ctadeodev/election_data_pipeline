{{ config(materialized='incremental') }}

with votes as (
    select
        vote_id,
        voter_id,
        candidate_id,
        election_id,
        vote_timestamp,
        updated_at
    from {{ ref('stg_votes') }}
    {% if is_incremental() %}
        where updated_at > (select coalesce(max(updated_at), '1900-01-01') from {{ this }})
    {% endif %}
),

votes_with_dimensions as (
    select
        v.vote_id,
        dv.voter_id,
        v.vote_timestamp,
        v.updated_at,
        dv.full_name as voter_name,
        dv.dob as voter_dob,
        dv.gender as voter_gender,
        dv.state as voter_state,
        dc.full_name as candidate_name,
        dc.party as candidate_party,
        de.election_name,
        de.election_date
    from votes v
    left join {{ ref('int_voters') }} dv on v.voter_id = dv.voter_id
    left join {{ ref('int_candidates') }} dc on v.candidate_id = dc.candidate_id
    left join {{ ref('int_elections') }} de on v.election_id = de.election_id
)

select * from votes_with_dimensions
