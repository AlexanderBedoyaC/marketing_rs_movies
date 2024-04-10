import pandas as pd
import numpy as np
import sqlite3 as sql
from a_funciones import ejecutar_sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
from sklearn.preprocessing import MinMaxScaler
from surprise import KNNBaseline
from surprise import Reader, Dataset

conn = sql.connect('data/db_movies')
cur = conn.cursor()
cur.execute('select name from sqlite_master where type = "table"')
cur.fetchall()

ejecutar_sql('c_Limpieza y Preprocesamiento.sql', cur)
movies_rating = pd.read_sql('SELECT * FROM movies_rating', conn)
movies_rating['date'] = pd.to_datetime(movies_rating['date'])
movies_rating['movieId'] = movies_rating['movieId'].astype(object)
movies_rating['userId'] = movies_rating['userId'].astype(object)
movies_rating['year'] = movies_rating['year'].astype(object)

query = '''
    SELECT DISTINCT year as year
    FROM movies_rating
    ORDER BY year DESC
    '''
years = pd.read_sql(query, conn)
decadas = [str(d) + '-' + str(d + 10) for d in range(1900, 2020, 10)]
years['decada'] = pd.cut(years.year.astype(int), len(decadas), labels = decadas)
query = '''
    SELECT date
    FROM movies_rating
    ORDER BY date DESC
    LIMIT 1;
    '''
ultimo_mes = pd.read_sql(query, conn).date.values[0].split('-')[1]
ultimo_anio = pd.read_sql(query, conn).date.values[0].split('-')[0]
query = '''
    SELECT `Género`
    FROM genres
    '''
genres = pd.read_sql(query, conn)
Genre = list(genres['Género'])
movies = pd.read_sql('SELECT * FROM movies2;', conn)
sc = MinMaxScaler()
movies_std = movies.drop(['movieId', 'title'], axis = 1)
movies_std[['year']] = sc.fit_transform(movies_std[['year']])
query = '''
    select distinct (userId) as user_id
    from movies_rating
    '''
usuarios = pd.read_sql(query,conn)
user_id = np.sort(list(usuarios['user_id'].value_counts().index))

def top10Views():
    query = '''
    SELECT title,
            avg(rating) AS rating_prom,
            count(*) AS view_num
    FROM movies_rating
    GROUP BY movieId
    ORDER BY view_num DESC
    LIMIT 10;
    '''

    return pd.read_sql(query, conn)

def top10Rating():
    query = '''
    SELECT title,
            avg(rating) AS rating_prom,
            count(*) AS view_num
    FROM movies_rating
    WHERE rating >= 1.0
    GROUP BY movieId
    HAVING view_num >= 30
    ORDER BY rating_prom DESC
    LIMIT 10;
    '''
    return pd.read_sql(query, conn)

def top10_dec_est():
    
    top10DecEst=pd.DataFrame()
    for d in decadas:
        c=d
        d = d.split('-')
        query = '''
        SELECT title,
            avg(rating) AS rating_prom,
            count(*) AS view_num
        FROM movies_rating
        WHERE year >= "{}" and year < "{}"
        GROUP BY movieId
        ORDER BY view_num DESC
        LIMIT 10;
        '''.format(d[0], d[1])
        df=pd.read_sql(query, conn)
        df['decada']=c
        top10DecEst=pd.concat([top10DecEst,df])
    
    return top10DecEst

def top10_rating_dec_est():
    top10RatingDecEst=pd.DataFrame()
    for d in decadas:
        c=d
        d = d.split('-')
        query = '''
        SELECT title,
            avg(rating) AS rating_prom,
            count(*) AS view_num
        FROM movies_rating
        WHERE year >= "{}" and year < "{}" and rating >= 1.0
        GROUP BY movieId
        HAVING view_num >= 30
        ORDER BY rating_prom DESC
        LIMIT 10;
        '''.format(d[0], d[1])
        df=pd.read_sql(query, conn)
        df['decada']=c
        top10RatingDecEst=pd.concat([top10RatingDecEst,df])
    return top10RatingDecEst

def top10Month():
    query = '''
    SELECT movieId, title,
            avg(rating) as rating_prom,
            count(movieId) as views_num
    FROM movies_rating
    WHERE strftime('%m', date) = "{}" and strftime('%Y', date) == "{}"
    GROUP BY movieId
    ORDER BY views_num DESC
    LIMIT 10;
    '''.format(ultimo_mes, ultimo_anio)
    return pd.read_sql(query, conn)

def top10Year():
    query = '''
    SELECT movieId, title,
            avg(rating) as rating_prom,
            count(movieId) as views_num
    FROM movies_rating
    WHERE strftime('%Y', date) == "{}"
    GROUP BY movieId
    ORDER BY views_num DESC
    LIMIT 10;
    '''.format(ultimo_anio)
    return pd.read_sql(query, conn)

def top10_views_genre():
    top10genre=pd.DataFrame()
    for genre in Genre:
        query = '''
        SELECT title,
                avg(rating) as rating_prom,
                sum({}) as views_num
        FROM movies_rating
        GROUP BY movieId
        ORDER BY views_num DESC
        LIMIT 10;
        '''.format(genre)
        df=pd.read_sql(query, conn)
        df['genero']=genre
        top10genre=pd.concat([top10genre,df])
    return top10genre

def top10_rating_genre():
    top10ratinggenre=pd.DataFrame()
    for genre in Genre:
        query = '''
        SELECT title,
                avg(rating) as rating_prom,
                sum({}) as views_num
        FROM movies_rating
        WHERE rating >= 1.0
        GROUP BY movieId
        HAVING views_num >= 30
        ORDER BY rating_prom DESC
        LIMIT 10;
        '''.format(genre)
        df=pd.read_sql(query, conn)
        df['genero']=genre
        top10ratinggenre=pd.concat([top10ratinggenre,df])
    return top10ratinggenre



def top10AllMovies():
    df=pd.DataFrame()
    for user in user_id:
        query = '''
        SELECT *
        FROM movies_rating
        WHERE userId = {} and rating >= 1.0;
        '''.format(user)
        ratings = pd.read_sql(query, conn)
        
        ###convertir ratings del usuario a array
        l_movies_r = ratings['movieId'].to_numpy()
        
        ###agregar la columna de movieId y título de la película a dummie para filtrar y mostrar nombre
        movies_std[['movieId','title']] = movies[['movieId','title']]
        
        ### filtrar películas calificados por el usuario
        movies_r = movies_std[movies_std['movieId'].isin(l_movies_r)]
        
        ## eliminar columna nombre e movieId
        movies_r = movies_r.drop(columns=['movieId','title'])
        movies_r["indice"] = 1 ### para usar group by y que quede en formato pandas tabla de centroide
        ##centroide o perfil del usuario
        centroide = movies_r.groupby("indice").mean()
        
        
        ### filtrar películas no leídos
        movies_nr = movies_std[~movies_std['movieId'].isin(l_movies_r)]
        ## eliminbar nombre e movieId
        movies_nr = movies_nr.drop(columns=['movieId','title'])
        
        ### entrenar modelo 
        model=neighbors.NearestNeighbors(n_neighbors=10, metric='cosine')
        model.fit(movies_nr)
        dist, idlist = model.kneighbors(centroide)
        
        ids = idlist[0] ### queda en un array anidado, para sacarlo
        recomend_b = movies.loc[ids][['title','movieId']]
        recomend_b['user']=user
        leidos = movies[movies['movieId'].isin(l_movies_r)][['title','movieId']]
        df=pd.concat([df,recomend_b])
        

    
    return df

top10view=top10Views()
top10rating=top10Rating()
top10dec=top10_dec_est()
top10ratingdec = top10_rating_dec_est()
top10year = top10Year()
top10month = top10Month()
top10genre = top10_views_genre()
top10ratinggenre = top10_rating_genre()
top10all = top10AllMovies()


top10view.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10view.csv')

top10rating.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10rating.csv')

top10dec.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10dec.csv')

top10ratingdec.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10ratingdec.csv')

top10year.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10year.csv')

top10month.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10month.csv')

top10genre.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10genre.csv')

top10ratinggenre.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10ratinggenre.csv')

top10all.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10all.csv')