SELECT 
    voter_id,
    election_id,
    COUNT(*) as count
FROM 
    {{ source('raw', 'votes') }}
GROUP BY 
    voter_id, 
    election_id
HAVING 
    COUNT(*) > 1
