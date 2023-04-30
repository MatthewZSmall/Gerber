/*
Part II:
You have portfolio data of different recency (as of date) in a database table.  Write a query that produces the latest available data for each portfolio.
*/

WITH ordered AS (
  SELECT
    as_of_date,
    portfolio,
    holding,
    other_fields,
    -- returns 1 for all holdings for the max as_of_date per portfolio
    RANK() OVER(PARTITION BY portfolio ORDER BY as_of_date DESC) AS rnk
  FROM
    table)
SELECT
  as_of_date,
  portfolio,
  holding,
  other_fields
FROM
  ordered
WHERE
  rnk = 1;
