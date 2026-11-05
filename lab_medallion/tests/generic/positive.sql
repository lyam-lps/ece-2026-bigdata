-- Generic test: fails on every row where the column is not strictly positive
{% test positive(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} <= 0
{% endtest %}
