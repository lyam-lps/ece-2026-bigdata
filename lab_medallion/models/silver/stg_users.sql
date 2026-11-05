with source as (
    select * from {{ source('bronze', 'users') }}
),

typed as (
    select
        cast(uuid as uuid) as user_id,
        trim(username) as username,
        trim(name) as name,
        upper(trim(sex)) as sex,
        lower(trim(mail)) as email,
        cast(birthdate as date) as birthdate,
        -- The address spans 2 lines: the street, then the city, the state and the zip code
        split_part(address, chr(10), 1) as street,
        split_part(address, chr(10), 2) as address_line_2
    from source
),

-- Exercise 3: date of the first order of each user
first_orders as (
    select
        user_id,
        min(ordered_at) as first_ordered_at
    from {{ ref('stg_orders') }}
    group by user_id
),

validated as (
    select
        t.*,
        -- Valid if known and not after the first order (users without orders are not constrained)
        t.birthdate is not null
            and (f.first_ordered_at is null or t.birthdate <= f.first_ordered_at) as birthdate_is_valid
    from typed t
    left join first_orders f on t.user_id = f.user_id
)

select
    user_id,
    username,
    -- Exercise 1: trimmed and lowercased username, for case-insensitive comparisons
    lower(trim(username)) as username_normalized,
    name,
    sex,
    email,
    -- Exercise 3: invalid birthdates are replaced with NULL
    case when birthdate_is_valid then birthdate end as birthdate,
    birthdate_is_valid,
    street,
    -- Military addresses, such as "DPO AE 12345", have no comma
    nullif(regexp_extract(address_line_2, '^(.+), [A-Z]{2} \d{5}$', 1), '') as city,
    regexp_extract(address_line_2, '([A-Z]{2}) (\d{5})$', 1) as state,
    regexp_extract(address_line_2, '([A-Z]{2}) (\d{5})$', 2) as zip_code
from validated
