select
    vote_id as id,
    voter_id,
    candidate_id,
    election_id,
    vote_timestamp as voted_at
from
    {{ source('election_source', 'votes') }}