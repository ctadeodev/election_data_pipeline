select
    candidate_id,
    full_name,
    party,
    election_id
from
    {{ source('election_source', 'candidates') }}