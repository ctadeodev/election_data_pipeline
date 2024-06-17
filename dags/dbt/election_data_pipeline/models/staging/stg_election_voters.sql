select
    voter_id,
    full_name,
    dob,
    gender,
    registration_date,
    state
from
    {{ source('election_source', 'voters') }}