import matplotlib.pyplot as plt
import networkx as nx
from flask import Flask, render_template, request
import sys
import json
import io
import base64



app=Flask(__name__)



class Videogame:
        def __init__(self, id, name, platform, year, genre, publisher):
            self.id = id
            self.name = name
            self.platform = platform
            self.genre = genre
            self.year = year
            self.publisher = publisher

        def getId(self):
            return self.id

        def getName(self):
            return self.name


        def getPlatform(self):
            return self.platform


        def getGenre(self):
            return self.genre

        def getYear(self):
            return self.year

        def getPublisher(self):
            return self.publisher

import csv

videogames = []

with open("app/vgsales.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        videogames.append(Videogame(len(videogames),row[1],row[2],row[3],row[4],row[5]))
    videogames.pop(0)


# Función para calcular el peso de una arista entre dos juegos
def compare_videogames(videogame1, videogame2):
    umbral_similitud = 0.2  # Umbral de similitud mínimo para crear una arista

    # Comparar el género
    if videogame1.getGenre() != videogame2.getGenre():
        return 0  # No hay similitud en el género, la arista no se crea

    similitud = 0

    # Comparar los demás atributos
    if videogame1.getPlatform() == videogame2.getPlatform():
        similitud += 0.3

    if abs(int(videogame1.getYear()) - int(videogame2.getYear())) <= 5:
        similitud += 0.2
    elif abs(int(videogame1.getYear()) - int(videogame2.getYear())) <= 15:
        similitud += 0.1

    if videogame1.getPublisher() == videogame2.getPublisher():
        similitud += 0.1

    if similitud < umbral_similitud:
        return 0  # No se supera el umbral de similitud, la arista no se crea


    return 1 - similitud

def create_graph(videogames):
    graph = {}
    for i, v1 in enumerate(videogames):
        if int(v1.id) not in graph:
            graph[int(v1.id)] = {}
        for j, v2 in enumerate(videogames):
            if i != j:
                weight = compare_videogames(v1, v2)
                if weight > 0:
                  graph[int(v1.id)][int(v2.id)] = weight

    return graph

graph = create_graph(videogames[:1500])

def prim_mst(graph, start_index):
    vertices = list(graph.keys())
    num_vertices = len(vertices)

    if num_vertices == 0:
        return []

    visited = [False] * num_vertices
    parent = [None] * num_vertices
    key = [sys.maxsize] * num_vertices

    key[start_index] = 0
    parent[start_index] = -1

    for _ in range(num_vertices - 1):
        min_key = sys.maxsize
        min_index = -1

        for i in range(num_vertices):
            if not visited[i] and key[i] < min_key:
                min_key = key[i]
                min_index = i

        visited[min_index] = True

        for vertex, weight in graph[vertices[min_index]].items():
            v_index = vertices.index(vertex)
            if not visited[v_index] and weight < key[v_index]:
                key[v_index] = weight
                parent[v_index] = min_index

    mst = []
    for i in range(num_vertices):
        if parent[i] is not None and parent[i] != -1:
          mst.append((vertices[parent[i]], vertices[i]))

    return mst



def grafiqueGraph(recomendations,start):
  recomendations.append(videogames[start])
  graphRecomend = create_graph(recomendations)
  nx_graph = nx.Graph(graphRecomend)

  # Dibujar el grafo
  #pos = nx.spring_layout(nx_graph)
  #nx.draw(nx_graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold', edge_color='gray')

  #Retrieve the weights from the graph dictionary
  edge_labels = {}
  for node1, edges in graphRecomend.items():
    for node2, weight in edges.items():
        edge_labels[(node1, node2)] = weight

  # Draw the graph
  pos = nx.spring_layout(nx_graph)
  nx.draw(nx_graph, pos, with_labels=True, node_color='#8b78a5', node_size=500, font_size=10, font_weight='bold', edge_color='gray', font_color='white')

  # Draw edge labels
  nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels)


  # Guardar la imagen en el disco
  image_path = 'app/static/img/graph.png'
  plt.savefig(image_path)

  plt.close()

  # Leer la imagen guardada y convertirla a base64
  with open(image_path, 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

  return image_base64 # Devolver la ruta de la imagen guardada




@app.route('/search', methods=['GET', 'POST'])
def index():


    if request.method == 'POST':
        if(request.form.get('inputValue')):
            input_value = request.form.get('inputValue')
        else:
            input_value=5

        if(request.form.get('searchedGame')):
                    searched_game = request.form.get('searchedGame')
                    #print(searched_game)
                    recomendations=[]
                    for videogame in videogames:
                        if searched_game == videogame.name:
                             videogameToList= videogame
                             mst = prim_mst(graph,int(videogame.id)-1)
                             for edge in mst:
                               if videogames[int(videogame.id)-1].genre==videogames[int(edge[1])-1].genre:
                                   recomendations.append(videogames[int(edge[1])-1])
                             image_base64 = grafiqueGraph(recomendations[:int(input_value)],int(videogame.id)-1)


                             break



        return render_template('index.html', videogames=recomendations, input_value=int(input_value), searched_game=searched_game, total_games=videogames[:1500], graph_image=image_base64, videogameToList= videogameToList)
    return render_template('index.html',videogames=videogames,input_value=5,searched_game="Mario", total_games=videogames[:1500])



@app.route('/specificSearch', methods=['GET', 'POST'])
def specificSearch():


    total_platforms = []

    for videogame in videogames[:1500]:
        if videogame.platform not in total_platforms:
            total_platforms.append(videogame.platform)

    if request.method == 'POST':
        if(request.form.get('inputValue')):
            input_value = request.form.get('inputValue')
        else:
            input_value=5

        if(request.form.get('searchedGame')):
                    searched_game = request.form.get('searchedGame')
                    #print(searched_game)
                    recomendations=[]
                    for videogame in videogames:
                        if searched_game == videogame.name:
                          videogameToList= videogame
                          mst = prim_mst(graph,int(videogame.id)-1)

                          if request.form.get('searchedPlatform'):
                                searched_platform = request.form.get('searchedPlatform')
                          else:
                                searched_platform = videogame.platform

                          for edge in mst:
                            if videogames[int(videogame.id)-1].genre==videogames[int(edge[1])-1].genre:
                                if videogames[int(edge[1])-1].platform == searched_platform:
                                    recomendations.append(videogames[int(edge[1])-1])
                          image_base64 = grafiqueGraph(recomendations[:int(input_value)],int(videogame.id)-1)


                          break



        return render_template('specificSearch.html', videogames=recomendations, input_value=int(input_value), searched_game=searched_game,searched_platform=searched_platform, total_games=videogames[:1500], graph_image=image_base64, total_platforms= total_platforms, videogameToList= videogameToList)
    return render_template('specificSearch.html',videogames=videogames,input_value=5,searched_game="Mario",searched_platform="Wii", total_games=videogames[:1500],total_platforms= total_platforms)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/graph')
def draw_graph():
    # Crear un objeto Graph de NetworkX
    graph2 = nx.Graph()

    # Agregar nodos y aristas al grafo (aquí deberías agregar tus propios datos)
    graph2.add_nodes_from([1, 2, 3])
    graph2.add_edges_from([(1, 2), (2, 3)])

    # Generar la imagen del gráfico utilizando matplotlib
    fig, ax = plt.subplots()
    nx.draw(graph2, with_labels=True, ax=ax)

    # Convertir la imagen a bytes
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Devolver la imagen como una respuesta HTTP
    return Response(buffer.getvalue(), mimetype='image/png')


if __name__=='__main__':
    app.run(debug=True, port=5000, threaded=True)


