/*
Part II:
You have portfolio data of different recency (as of date) in a database table.  Write a query that produces the latest available data for each portfolio.
*/

WITH ordered AS (
  SELECT
    as_of_date,
    portfolio,
    holding,
    -- RANK() return 1 for all holdings for the max as_of_date per portfolio
    RANK() OVER(PARTITION BY portfolio ORDER BY as_of_date DESC) AS rn
  FROM
    table)
SELECT
  as_of_date,
  portfolio,
  holding
FROM
  ordered
WHERE
  rn = 1;
