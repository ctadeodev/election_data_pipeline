with source as (
    select * from {{ source('raw', 'candidates') }}
)

select * from source
{% if is_incremental() %}
    where updated_at > (select coalesce(max(updated_at), '1900-01-01') from {{ this }})
{% endif %}
