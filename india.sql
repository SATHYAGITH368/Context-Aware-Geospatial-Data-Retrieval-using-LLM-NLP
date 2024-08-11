-- Drop the existing table if it exists
DROP TABLE IF EXISTS cities;

-- Create the new cities table
CREATE TABLE cities (
    city VARCHAR(100),
    lat NUMERIC,
    lng NUMERIC,
    country VARCHAR(100),
    iso2 VARCHAR(2),
    admin_name VARCHAR(100),
    capital VARCHAR(10),
    population BIGINT,
    population_proper BIGINT

);

-- Import data from CSV into the cities table using \copy
COPY cities(city, lat, lng, country, iso2, admin_name, capital, population, population_proper)
FROM '/Users/sathya/Downloads/in.csv' DELIMITER ',' CSV HEADER;

