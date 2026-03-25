CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS doc_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS recipes (
    recipe_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    unit VARCHAR(50),
    sugar_per_unit DECIMAL(10, 4) DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    sugar_g DECIMAL(10, 2),
    brew_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc_id ON doc_chunks (doc_id);

INSERT INTO ingredients (name, unit, sugar_per_unit)
VALUES
    ('Espresso Shot', 'shot', 0.0),
    ('Fresh Coconut Water', 'ml', 0.04),
    ('Coconut Meat', 'g', 0.05),
    ('Concentrated Coffee', 'ml', 0.0),
    ('Coconut Milk', 'ml', 0.03),
    ('Condensed Milk', 'ml', 0.70),
    ('Thai Tea Base', 'ml', 0.0),
    ('Fresh Milk', 'ml', 0.05),
    ('Sugar', 'g', 1.0),
    ('Caramel Syrup', 'ml', 0.80),
    ('Cocoa Powder', 'g', 0.10),
    ('Matcha Powder', 'g', 0.0),
    ('Orange Juice', 'ml', 0.12),
    ('Tonic Water', 'ml', 0.0),
    ('Lemon Juice', 'ml', 0.02),
    ('Strawberry Syrup', 'ml', 0.75),
    ('Blueberry Syrup', 'ml', 0.75),
    ('Soda Water', 'ml', 0.0),
    ('Vanilla Ice Cream', 'scoop', 0.15),
    ('Water', 'ml', 0.0),
    ('Milk Foam', 'ml', 0.05)
ON CONFLICT (name) DO UPDATE
SET unit = EXCLUDED.unit,
    sugar_per_unit = EXCLUDED.sugar_per_unit;

INSERT INTO recipes (name, description, price)
VALUES
    ('Iced Coconut Americano', 'Americano with fresh coconut water and coconut meat.', 85.0),
    ('Coconut Frozen Coffee', 'Frozen coffee blended with coconut milk and condensed milk.', 95.0),
    ('Thai Tea Latte', 'Creamy Thai tea latte.', 65.0),
    ('Coconut Latte', 'Latte with coconut notes and fresh milk.', 90.0),
    ('Dirty Coconut Coffee', 'Layered coconut milk and espresso drink.', 95.0),
    ('Espresso', 'Classic espresso shot.', 50.0),
    ('Americano (Hot)', 'Hot Americano.', 55.0),
    ('Americano (Iced)', 'Iced Americano.', 60.0),
    ('Latte', 'Milk-based coffee.', 65.0),
    ('Cappuccino', 'Coffee with milk foam.', 70.0),
    ('Mocha', 'Coffee with cocoa.', 75.0),
    ('Caramel Macchiato', 'Coffee with caramel syrup.', 80.0),
    ('Green Tea Latte', 'Matcha latte.', 65.0),
    ('Cocoa', 'Rich iced cocoa.', 60.0),
    ('Lemon Tea', 'Refreshing lemon tea.', 50.0),
    ('Italian Soda Strawberry', 'Strawberry soda.', 55.0),
    ('Italian Soda Blueberry', 'Blueberry soda.', 55.0),
    ('Dirty Coffee', 'Cold milk topped with fresh espresso.', 85.0),
    ('Affogato', 'Vanilla ice cream with espresso.', 95.0),
    ('Cold Brew Orange', 'Cold brew coffee with orange juice.', 110.0),
    ('Espresso Tonic', 'Espresso with tonic water.', 90.0)
ON CONFLICT (name) DO UPDATE
SET description = EXCLUDED.description,
    price = EXCLUDED.price;

INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount)
SELECT r.recipe_id, i.ingredient_id, v.amount
FROM (
    VALUES
        ('Iced Coconut Americano', 'Espresso Shot', 2.00),
        ('Iced Coconut Americano', 'Fresh Coconut Water', 120.00),
        ('Iced Coconut Americano', 'Coconut Meat', 20.00),
        ('Coconut Frozen Coffee', 'Concentrated Coffee', 60.00),
        ('Coconut Frozen Coffee', 'Coconut Milk', 60.00),
        ('Coconut Frozen Coffee', 'Condensed Milk', 30.00),
        ('Thai Tea Latte', 'Thai Tea Base', 100.00),
        ('Thai Tea Latte', 'Fresh Milk', 50.00),
        ('Coconut Latte', 'Espresso Shot', 1.00),
        ('Coconut Latte', 'Fresh Milk', 100.00),
        ('Coconut Latte', 'Fresh Coconut Water', 50.00),
        ('Espresso', 'Espresso Shot', 1.00),
        ('Americano (Hot)', 'Espresso Shot', 1.00),
        ('Americano (Hot)', 'Water', 150.00),
        ('Americano (Iced)', 'Espresso Shot', 2.00),
        ('Americano (Iced)', 'Water', 120.00),
        ('Latte', 'Espresso Shot', 1.00),
        ('Latte', 'Fresh Milk', 150.00),
        ('Cappuccino', 'Espresso Shot', 1.00),
        ('Cappuccino', 'Fresh Milk', 100.00),
        ('Cappuccino', 'Milk Foam', 50.00),
        ('Mocha', 'Espresso Shot', 1.00),
        ('Mocha', 'Fresh Milk', 100.00),
        ('Mocha', 'Cocoa Powder', 15.00),
        ('Caramel Macchiato', 'Espresso Shot', 1.00),
        ('Caramel Macchiato', 'Fresh Milk', 120.00),
        ('Caramel Macchiato', 'Caramel Syrup', 25.00),
        ('Green Tea Latte', 'Matcha Powder', 10.00),
        ('Green Tea Latte', 'Fresh Milk', 150.00),
        ('Cocoa', 'Cocoa Powder', 20.00),
        ('Cocoa', 'Fresh Milk', 150.00),
        ('Cocoa', 'Sugar', 20.00),
        ('Lemon Tea', 'Thai Tea Base', 100.00),
        ('Lemon Tea', 'Lemon Juice', 20.00),
        ('Lemon Tea', 'Sugar', 15.00),
        ('Italian Soda Strawberry', 'Strawberry Syrup', 30.00),
        ('Italian Soda Strawberry', 'Soda Water', 150.00),
        ('Italian Soda Blueberry', 'Blueberry Syrup', 30.00),
        ('Italian Soda Blueberry', 'Soda Water', 150.00),
        ('Dirty Coffee', 'Espresso Shot', 1.00),
        ('Dirty Coffee', 'Fresh Milk', 120.00),
        ('Affogato', 'Espresso Shot', 1.00),
        ('Affogato', 'Vanilla Ice Cream', 1.00),
        ('Cold Brew Orange', 'Concentrated Coffee', 60.00),
        ('Cold Brew Orange', 'Orange Juice', 120.00),
        ('Espresso Tonic', 'Espresso Shot', 2.00),
        ('Espresso Tonic', 'Tonic Water', 150.00),
        ('Dirty Coconut Coffee', 'Espresso Shot', 1.00),
        ('Dirty Coconut Coffee', 'Coconut Milk', 120.00)
) AS v(recipe_name, ingredient_name, amount)
JOIN recipes r ON r.name = v.recipe_name
JOIN ingredients i ON i.name = v.ingredient_name
ON CONFLICT (recipe_id, ingredient_id) DO UPDATE
SET amount = EXCLUDED.amount;

INSERT INTO products (name, category, price, sugar_g, brew_count)
VALUES
    ('Americano', 'Coffee', 60.0, 0.0, 0),
    ('Hot Latte', 'Coffee', 65.0, 14.5, 0),
    ('Matcha Latte', 'Tea', 65.0, 41.5, 0),
    ('Thai Tea', 'Tea', 65.0, 60.5, 0),
    ('Caramel Macchiato', 'Coffee', 80.0, 69.5, 0),
    ('Dirty Coffee', 'Coffee', 85.0, 18.0, 0),
    ('Cocoa', 'Chocolate', 60.0, 30.0, 0),
    ('Espresso Tonic', 'Coffee', 90.0, 8.0, 0),
    ('Italian Soda Strawberry', 'Soda', 55.0, 22.5, 0),
    ('Italian Soda Blueberry', 'Soda', 55.0, 22.5, 0)
ON CONFLICT (name) DO UPDATE
SET category = EXCLUDED.category,
    price = EXCLUDED.price,
    sugar_g = EXCLUDED.sugar_g,
    brew_count = EXCLUDED.brew_count;
