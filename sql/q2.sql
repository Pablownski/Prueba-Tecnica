SELECT
    category,
    COUNT(*)                                    AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM products
GROUP BY category
ORDER BY percentage DESC;