
/* Crear nueva tabla movies extrayendo año, título y los géneros como columnas individuales */
DROP TABLE IF EXISTS movies2;
CREATE TABLE  movies2 AS
SELECT movieId,
        CASE WHEN SUBSTR(RTRIM(title, ' '), -6, 1) = '('
                THEN SUBSTR(RTRIM(title, ' '), -5, 4)
                ELSE 1900
                END AS year,
        RTRIM(title, ' ') as title,
        CASE WHEN genres LIKE '%Action%' THEN 1 ELSE 0 END AS `Action`,
        CASE WHEN genres LIKE '%Adventure%' THEN 1 ELSE 0 END AS Adventure,
        CASE WHEN genres LIKE '%Animation%' THEN 1 ELSE 0 END AS Animation,
        CASE WHEN genres LIKE '%Children%' THEN 1 ELSE 0 END AS Children,
        CASE WHEN genres LIKE '%Comedy%' THEN 1 ELSE 0 END AS Comedy,
        CASE WHEN genres LIKE '%Crime%' THEN 1 ELSE 0 END AS Crime,
        CASE WHEN genres LIKE '%Documentary%' THEN 1 ELSE 0 END AS Documentary,
        CASE WHEN genres LIKE '%Drama%' THEN 1 ELSE 0 END AS Drama,
        CASE WHEN genres LIKE '%Fantasy%' THEN 1 ELSE 0 END AS Fantasy,
        CASE WHEN genres LIKE '%Film-Noir%' THEN 1 ELSE 0 END AS Film_Noir,
        CASE WHEN genres LIKE '%Horror%' THEN 1 ELSE 0 END AS Horror,
        CASE WHEN genres LIKE '%IMAX%' THEN 1 ELSE 0 END AS IMAX,
        CASE WHEN genres LIKE '%Musical%' THEN 1 ELSE 0 END AS Musical,
        CASE WHEN genres LIKE '%Mystery%' THEN 1 ELSE 0 END AS Mystery,
        CASE WHEN genres LIKE '%Romance%' THEN 1 ELSE 0 END AS Romance,
        CASE WHEN genres LIKE '%Sci-Fi%' THEN 1 ELSE 0 END AS Sci_Fi,
        CASE WHEN genres LIKE '%Thriller%' THEN 1 ELSE 0 END AS Thriller,
        CASE WHEN genres LIKE '%War%' THEN 1 ELSE 0 END AS War,
        CASE WHEN genres LIKE '%Western%' THEN 1 ELSE 0 END AS Western,
        CASE WHEN genres LIKE '%(no genres listed)%' THEN 1 ELSE 0 END AS Desconocido
FROM movies;

/* Crear nueva tabla ratings formateando la fecha */
DROP TABLE IF EXISTS ratings2;
CREATE TABLE ratings2 AS
SELECT userId, movieId, rating,
        strftime('%Y-%m-%d', datetime(timestamp, 'unixepoch')) AS date
FROM ratings;

/* Crear nueva tabla que una las tablas movies y ratings por medio del movieId */
DROP TABLE IF EXISTS movies_rating;
CREATE TABLE movies_rating AS
SELECT mv.*, rt.userId, rt.rating, rt.date
FROM ratings2 AS rt
LEFT JOIN movies2 as mv
ON rt.movieId = mv.movieId;

