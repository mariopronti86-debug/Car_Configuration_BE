-- INSERT INTO app_user (tipo, email, password_hash) VALUES
--     ('admin',  'admin@autoelite.it',    '$2b$12$QFt0hgM/70Sl2TioFaOg9OoL4Qud.gn31s1AVpV8M5V4VwAiinpGO'),
--     ('client', 'mario.rossi@email.com', '$2b$12$5TTcz4NDQHjnjWKg6A30suidL.nIyatTNLRlY1ZG9INmaEQha1WIK');

-- INSERT INTO admin  (admin_id)  VALUES (1);
-- INSERT INTO client (client_id, first_name, last_name, phone) VALUES
--     (2, 'Mario', 'Rossi', '333-1234567');

-- INSERT INTO engine (fuel_type, power_hp, extra_price) VALUES
--     ('Benzina',   150,     0.00),
--     ('Diesel',    200,  2000.00),
--     ('Elettrico', 300,  8000.00),
--     ('Ibrido',    250,  5000.00);

-- INSERT INTO model (name, brand, base_price, category, engine_id) VALUES
--     ('A3 Sportback', 'Audi', 35000.00, 'Berlina', 1),
--     ('Q5',           'Audi', 55000.00, 'SUV',     2),
--     ('Serie 3',      'BMW',  40000.00, 'Berlina', 1),
--     ('X5',           'BMW',  65000.00, 'SUV',     3);

-- INSERT INTO optional (name, category, price) VALUES
--     ('Cerchi in lega 18"',        'Cerchi',    800.00),
--     ('Cerchi in lega 20"',        'Cerchi',   1200.00),
--     ('Tetto panoramico',          'Esterno',  2500.00),
--     ('Verniciatura metallizzata', 'Esterno',   600.00),
--     ('Sedili in pelle',           'Interni',  1800.00),
--     ('Sedili riscaldati',         'Interni',   500.00),
--     ('Sistema audio premium',     'Optional', 1200.00),
--     ('Telecamera posteriore',     'Optional',  400.00),
--     ('Navigatore integrato',      'Optional',  900.00),
--     ('Pacchetto Sport',           'Optional', 3000.00);

-- -- Tutti i modelli hanno tutti gli optional disponibili
-- INSERT INTO model_optional (model_id, optional_id) VALUES
--     (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),
--     (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(2,10),
--     (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,10),
--     (4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10);

-- INSERT INTO compatibility_rule (rule_type) VALUES
--     ('incompatible'),
--     ('requires');

-- -- Cerchi 18" e 20" sono incompatibili
-- INSERT INTO compatibility (optional_id, optional_with_id, rule_id) VALUES (1, 2, 1);

-- -- Sedili riscaldati richiedono sedili in pelle
-- INSERT INTO compatibility (optional_id, optional_with_id, rule_id) VALUES (6, 5, 2);
