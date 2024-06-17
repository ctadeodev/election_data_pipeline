SELECT 
    voter_id,
    election_id,
    COUNT(*) as count
FROM 
    {{ source('election_source', 'votes') }}
GROUP BY 
    voter_id, 
    election_id
HAVING 
    COUNT(*) > 1
