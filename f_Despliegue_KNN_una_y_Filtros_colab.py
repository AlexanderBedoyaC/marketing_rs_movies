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

def top10PreRating():
    df=pd.read_sql('select * from movies_rating where rating>=1', conn)
    reader = Reader(rating_scale=(1,5))
    ratings=df[['userId','movieId','rating']]
    data   = Dataset.load_from_df(ratings[['userId','movieId','rating']], reader)
    model = KNNBaseline(sim_options = {'name': 'msd', 'min_support': 2, 'user_based': False})
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

top10one = top10OneMovie()
top10pred = top10PreRating()


top10one.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10one.csv')

top10pred.to_csv('C:\\Users\\Usuario\\OneDrive - Universidad de Antioquia\\Documentos\\Universidad\\Analitica3\\marketing_rs_movies\\salidas\\top10pred.csv')