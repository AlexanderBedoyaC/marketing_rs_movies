import pandas as pd
import numpy as np
import sqlite3 as sql
from a_funciones import ejecutar_sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
from sklearn.preprocessing import MinMaxScaler

conn = sql.connect('data/db_movies')
cur = conn.cursor()
cur.execute('select name from sqlite_master where type = "table"')
cur.fetchall()

ejecutar_sql('d_Limpieza y Preprocesamiento.sql', cur)
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

def top10OneMovie():
    
    model = neighbors.NearestNeighbors(n_neighbors = 11, metric='cosine')
    model.fit(movies_std)
    dist, idlist = model.kneighbors(movies_std)
    distancias = pd.DataFrame(dist)
    id_list = pd.DataFrame(idlist)
    movies_name = np.sort(list(movies['title'].value_counts().index))
    df3=pd.DataFrame()
    for movie in movies_name:
        movies_list_name = []
        movies_id = movies[movies['title'] == movie].index
        movies_id = movies_id[0]
        for newid in idlist[movies_id]:
            movies_list_name.append(movies.loc[newid].title)
        df = pd.DataFrame()
        df['Movie'] = movies_list_name
        df2 = df.drop(df[df['Movie'] == movie].index)
        df2['recomendfor']=movie
        df3=pd.concat([df3,df2])
        
        
    return df3

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

def top10PreRating():
    df=pd.read_sql('select * from movies_rating where rating>=1', conn)
    reader = Reader(rating_scale=(1,5))
    ratings=df[['userId','movieId','rating']]
    data   = Dataset.load_from_df(ratings[['userId','movieId','rating']], reader)
    model= KNNBasic(sim_options = {'name': 'msd', 'min_support': 2, 'user_based': False})
    trainset = data.build_full_trainset()
    model=model.fit(trainset)
    predset = trainset.build_anti_testset()
    predictions = model.test(predset)
    predictions_df = pd.DataFrame(predictions)
    df=pd.DataFrame()
    for user in user_id:
        predictions_userID = predictions_df[predictions_df['uid'] == int(user)].\
                        sort_values(by="est", ascending = False).head(10)

        rec = predictions_userID[['iid','est']]
        
        recomendados=pd.merge(movies[['movieId','title']],rec,left_on='movieId', right_on='iid', how='right')
        recomendados['user']=user
        df=pd.concat([df,recomendados[['title','est']]])


    return(df)

top10view=top10Views()
top10rating=top10Rating()
top10dec=top10_dec_est()
top10ratingdec = top10_rating_dec_est()
top10year = top10Year()
top10month = top10Month()
top10genre = top10_views_genre()
top10ratinggenre = top10_rating_genre()
top10one = top10OneMovie()
top10all = top10AllMovies()
top10pred = top10PreRating() 


top10view.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10view.csv')

top10rating.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10rating.csv')

top10dec.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10dec.csv')

top10ratingdec.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10ratingdec.csv')

top10year.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10year.csv')

top10month.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10month.csv')

top10genre.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10genre.csv')

top10ratinggenre.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10ratinggenre.csv')

top10one.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10one.csv')

top10all.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10all.csv')

top10pred.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10pred.csv')