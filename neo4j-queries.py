from neo4j import GraphDatabase
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

def addNodeWithNewAuthor(tx,ISBN,titulo,año_publi,id_autor,nombre_autor):
    query = (
        "MERGE (a:Autores{id_autor:$id_autor,nombre:$nombre_autor})"
        "MERGE (l:Libros {ISBN: toInteger($ISBN),titulo: $titulo,año_publi: $año_publi})"
        "MERGE (l)-[:AUTOR]->(a)"
        )
    tx.run(query,id_autor=id_autor,titulo=titulo,año_publi=año_publi,ISBN =ISBN,nombre_autor=nombre_autor)
    

def addNodeWithExistingAuthor(tx,ISBN,titulo,año_publi,nombre_autor):
    query = ("  MATCH (a:Autores {nombre:$nombre_autor})"
             "MERGE (l:Libros {ISBN: toInteger($ISBN),titulo: $titulo,año_publi: $año_publi})"
             "MERGE (l)-[:AUTOR]->(a)"
             )
    tx.run(query,titulo=titulo,año_publi=año_publi,ISBN =ISBN,nombre_autor=nombre_autor)
    

df = pd.read_csv("./books.csv",sep=";",on_bad_lines='skip',encoding='latin-1')
url = "bolt://localhost:7687"
usuario = "neo4j"
password = "master22"
json_autores = []
count_authors = 0
count = 0
with GraphDatabase.driver(url,auth=(usuario,password)) as GraphDriver:
    for index,row in df.iterrows():
        with GraphDriver.session() as session:
            if count >= 100:
                break
            try:
                int(row["ISBN"])
            except:
                continue
            id = checkIfExists(json_autores,row["Book-Author"])
            if id > count_authors:
                count_authors +=1
                #Aquí el autor no existe por lo que hay que añadir el nuevo registro
                session.execute_write(
                                    addNodeWithNewAuthor,
                                    int(row["ISBN"]),
                                    row["Book-Title"],
                                    int(row["Year-Of-Publication"]),
                                    id,
                                    row["Book-Author"])
                author = {
                "id_autor":int(id),
                "nombre_autor":str(row["Book-Author"])
                }
                json_autores.append(author)
            else:
                session.execute_write(
                                addNodeWithExistingAuthor,
                                int(row["ISBN"]),
                                row["Book-Title"],
                                int(row["Year-Of-Publication"]),
                                row["Book-Author"])
                print("Repetido: ",str(row["Book-Author"]))
                ##Aquí meter el autor si existe

            count +=1

print("Succesfully finish") 
