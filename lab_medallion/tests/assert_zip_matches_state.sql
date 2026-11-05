{{ config(severity='warn') }}

-- A ZIP code must fall within one of the ranges assigned to the user's state
-- The test fails (warns) for every user whose ZIP code matches no range of their state
select
    u.user_id,
    u.state,
    u.zip_code
from {{ ref('stg_users') }} u
where u.zip_code is not null
  and u.zip_code <> ''
  and not exists (
      select 1
      from {{ ref('zip_ranges') }} r
      where r.state = u.state
        and cast(u.zip_code as integer) between r.zip_min and r.zip_max
  )
