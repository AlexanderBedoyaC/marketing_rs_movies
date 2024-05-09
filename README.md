# Proyecto de aplicación de Analítica en Marketing

## Integrantes

Ana María Ospina Arredondo

Brahayan Stiven Gil Henao

Jhon Alexander Bedoya Carvajal

Sebastián Salamanca Mendez

# Sistema de recomendación para películas

## Descripción del problema y de los datos

Una plataforma online quiere tener una solución que le permita hacer recomendaciones de películas a sus usuarios,
con el objetivo de que estos tengan una mejor experiencia, y esto permita mejorar su fidelización y recomendación a nuevos clientes. Cada equipo
de trabajo será el encargado de diseñar un sistema que permita hacer recomendaciones a los clientes.

La empresa cuenta con una base de datos sql “bd_movies” en la cuál se encuentran dos tablas.

Una tabla tiene la información del catálogo de películas disponibles en la plataforma llamada ‘movies’. Los campos que tiene esta tabla son:

- movieId: código que identifica la película.

- title: Nombre y año de la película.

- genres: Lista de géneros a los que pertenece la película.


La segunda tabla es una lista de los usuarios y las películas que vieron, las fechas en las que las vieron y la calificación que le dieron a
la película. Los campos son:

- userId: Código que identifica al usuario.

- movieId: Código que identifica la película.

- Rating: Calificación de la película vista de 1 a 5.

- Timestamp: Timestamp de la fecha en la que fue vista la película.

