SELECT count(*) AS recipes_count FROM recipes;
SELECT count(*) AS ingredients_count FROM ingredients;
SELECT count(*) AS recipe_ingredients_count FROM recipe_ingredients;

SELECT name, category, price, sugar_g
FROM products
ORDER BY sugar_g DESC, price DESC;

SELECT
    r.name AS recipe_name,
    sum(ri.amount * i.sugar_per_unit) AS estimated_sugar
FROM recipes r
JOIN recipe_ingredients ri ON ri.recipe_id = r.recipe_id
JOIN ingredients i ON i.ingredient_id = ri.ingredient_id
GROUP BY r.name
ORDER BY estimated_sugar DESC NULLS LAST, r.name;
