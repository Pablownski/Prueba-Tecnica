SELECT *
FROM (
    SELECT
        id,
        name,
        price,
        category,
        source,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rank
    FROM products
)
WHERE rank <= 10
ORDER BY category, price DESC;