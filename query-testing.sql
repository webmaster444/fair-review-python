SELECT p.ID, p.name AS product_name, COUNT(pr.ID) AS num_reviews, AVG(pr.rate) AS overall_rate
FROM products p
JOIN product_reviews pr ON p.ID = pr.`Product ID`
JOIN product_tags pt ON p.ID = pt.`Product ID`
JOIN tags t ON pt.`Tag ID` = t.ID
WHERE p.name LIKE '%pt%'
  AND t.`Tag Name` IN ('tags1', 'tags2')
GROUP BY p.ID
HAVING num_reviews > 3 AND overall_rate > 3;




SELECT p.product_id, p.name AS product_name, num_reviews, overall_rate
FROM products p
JOIN (
  SELECT pr.product_id, COUNT(pr.review_id) AS num_reviews, AVG(pr.rate) AS overall_rate
  FROM product_reviews pr
  GROUP BY pr.product_id
) AS review_info ON p.product_id = review_info.product_id
JOIN product_tags pt ON p.product_id = pt.product_id
JOIN tags t ON pt.tag_id = t.tag_id
WHERE p.name LIKE '%pt%'
  AND t.tag_name IN ('awesome', 'electronics')
  AND overall_rate > 3;
  AND num_reviews > 3

SELECT
    p.ID,
    p.Name,
    GROUP_CONCAT(DISTINCT(t.`Tag Name`)) AS tags,
    COUNT(pr.Title) / COUNT(DISTINCT(t.`Tag Name`)) AS number_of_reviews,
    AVG(pr.rate) AS overall_rate
FROM
    products p
LEFT JOIN
    product_tags pt ON p.ID = pt.`Product ID`
LEFT JOIN
    tags t ON pt.`Tag ID` = t.ID
LEFT JOIN
    product_reviews pr ON p.ID = pr.`Product ID`
WHERE
    p.name LIKE '%PT%'
    AND (t.`Tag Name` = 'tags1' OR t.`Tag Name` = 'tags2' OR t.`Tag Name` = 'tags3')
GROUP BY p.ID
ORDER BY
    p.ID, t.`ID`;