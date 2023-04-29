/*
Part II:
You have portfolio data of different recency (as of date) in a database table.  Write a query that produces the latest available data for each portfolio.
*/

WITH ordered AS (
  SELECT
    portfolio,
    other_fields,
    as_of_date,
    -- use ROW_NUMBER() instead of RANK() or DENSE_RANK() to avoid ties
    ROW_NUMBER() OVER(PARTITION BY portfolio ORDER BY as_of_date DESC) AS rn
  FROM
    table)
SELECT
  portfolio,
  other_fields,
  as_of_date
FROM
  ordered
WHERE
  rn = 1;
