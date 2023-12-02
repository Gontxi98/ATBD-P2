import pymongo
import pandas as pd
import json

#Esta función recorre de todos los jsons de autores, para obtener la nueva id, en caso de que exista devuelve la id sino devuelve nueva id
def checkIfExists(json_autores,nuevo_autor:str):
    id = 1
    if json_autores != []:
        for json in json_autores:
               
            if json["nombre_autor"] == nuevo_autor:
                return json["id_autor"] 
            id+=1

    return id

df = pd.read_csv("./books.csv",sep=";",on_bad_lines='skip',encoding='latin-1')

client = pymongo.MongoClient("localhost",27017)
database_name = "booksDB"
db = client[database_name]
autor_collection = db["Autores"]
book_collection = db["Libros"]
json_autores = []
count_authors = 0
count = 0
for index,row in df.iterrows():
    if count >= 100:
        break
    try:
        int(row["ISBN"])
    except:
        continue
    id = checkIfExists(json_autores,row["Book-Author"])
    if id > count_authors:
        count_authors +=1
        author = {
            "id_autor":int(id),
            "nombre_autor":str(row["Book-Author"])
        }
        json_autores.append(author)
        autor_collection.insert_one(author)
    else:
        print("Repetido: ",str(row["Book-Author"]))
        ##Aquí meter el autor si existe
    book = {"isbn":int(row["ISBN"]),
            "titulo":str(row["Book-Title"]),
            "año_edicion":int(row["Year-Of-Publication"]),
            "id_autor": int(id)
            }
    book_collection.insert_one(book)
    count +=1

print("Succesfully finish") 
