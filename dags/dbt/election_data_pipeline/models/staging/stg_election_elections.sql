select
    election_id as id,
    election_name as name,
    election_date as date
from
    {{ source('election_source', 'elections') }}