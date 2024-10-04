Cria um programa servidor Flask na porta 44444 usando python (server.py). 


# Base de dados

Ao iniciar o servidor lê todos os arquivos JSON de uma pasta definida na variável JSON_DB_DIR, 
cada arquivo JSON é uma base de dados diferente e tem o seguinte formato

{
    "dataset_name":"NAMEDB",
    "labels":["positive","negative","neutral","pain","other"],
    "base_dir":"/some/path/directory",
    "samples": [
        {"filepath":"relative/path/of/image1.png", "label":"neutral"},
        {"filepath":"relative/path/of/image2.jpeg", "label":""},
        {"filepath":"relative/path/of/image3.bmp", "label":"positive"}
    ]
}

O servidor usa bases de dados SQLite que estarão armazenadas na pasta SQLITE_DB_DIR.
O servidor tentara criar uma base de dados SQLite por cada JSON do diretório JSON_DB_DIR.
* Se a base de dados não existe uma função do servidor cria uma com as características descritas no JSON
* Se a base de dados já existe uma função do servidor verificará que todos os "filepath" do JSON existam na base de dados SQLite, se este nao existe o agrega a base de dados.

Cada base de dados vai criar três tabelas: uma para os metadados ("dataset_name", "base_dir"), outra para "labels" e outra para os "samples"

No programa servidor evita salvar em memoria RAM a informação de "samples" dos JSON, para isso você tem as bases de dados SQLite, assim poupamos memoria RAM pois samples tem muitos dados.

Não dependas dos JSON para saber quantas bases de dados se tem e as informações de cabeçalho da base de dados, para obter essas informações vê a SQLITE_DB_DIR. A pasta JSON_DB_DIR é só para passar informações iniciais ao servidor, um usuário externo pode apagar os arquivos mas as bases SQLite permanecem 

# Seguridade

O servidor deve ter uma lista de usuários permitidos, cada usuário tem um password.
Ao iniciar o servidor este lê todos os arquivos JSON de uma pasta definida na variável JSON_USER_DIR,
onde cada arquivo JSON é um usuário diferente e tem o seguinte formato

{
    "user":"nome de usuario",
    "password":"fr@441$"
}

# Comandos do servidor
O servidor recebe 3 comandos "SIZE", "OBTAIN" e "CLASSIFY", 
em todos os casos as credenciais são enviada no cabeçalho da consulta.

* "SIZE": onde o servidor recebe um JSON com o seguinte formato

{
    "dataset_name":"NAMEDB"
}

e o servidor responde com um JSON com o seguinte formato

{
    "dataset_name":"NAMEDB"
    "size":1024
}

onde "size" indica a quantidade de elementos que a base de dados "dataset_name" tem em "samples".

* "OBTAIN": onde o servidor recebe um JSON com o seguinte formato

{
    "dataset_name":"NAMEDB"
    "id":-1
}
onde "dataset_name" é o nome da base de dados que se deseja consultar e "id" é a posição do elemento em "samples" que quero obter.

Se a posição do "id" existe em "samples", o servidor responde enviando a imagem binaria no path formado pela junção de "base_dir" e "filepath" dessa posição de "id" e um JSON que tem o seguinte formato 

{
    "dataset_name":"NAMEDB",
    "base_dir":"/some/path/directory",
    "filepath":"relative/path/of/image-n.png", 
    "labels":["positive","negative","neutral","pain","other"]
}

Se a posição do "id" NÃO existe em "samples" (por exemplo "id"< 0), o servidor asume que o "id" em consulta é a posição do primeiro elemento em "samples" que tem um "label" vazio.

* "CLASSIFY": onde o servidor recebe um JSON com o formato 
{
    "dataset_name":"NAMEDB",
    "base_dir":"/some/path/directory",
    "filepath":"relative/path/of/image-n.png", 
    "label":"positive"
}

Com estas informações existem duas possíveis respostas do servidor

* O servidor responde {"response":true}  quando existe "dataset_name" com nome "NAMEDB", com um "base_dir" com conteúdo "/some/path/directory", dentro de "samples" existe um path relativo "filepath" igual a "relative/path/of/image-n.png" e o "label" existe em "labels".
Nesse caso o servidor modifica a base de dados "dataset_name" modificando o "label" do "filepath" indicado.

* Caso contrario o servidor responde  {"response":false} e não faz nada.

# programas auxiliares

* Cria um programa cliente de exemplo, client.py , ao criar o cliente agrupa as funções de consulta de modo que o mesmo script serva de modulo (API) para o servidor. Presta especial atenção ao comando "OBTAIN" pois este comando recebe duas coisas uma imagem binaria e um json.

* Cria um programa,export_csv.py, ao qual lhe entrego o diretório de entrada SQLITE_DB_DIR, um nome "dataset_name", uma pasta de saída "OUTPUT_DIR" e um filename "some_name.csv", 
e o programa cria um arquivo CSV "some_name.csv" no diretório "OUTPUT_DIR" com colunas preenchidas com os elementos de "filepath" e "label" de "samples". Adicionalmente cria o arquivo "some_name.csv.json" com as informações ("dataset_name","base_dir","labels") extraídas da base de dados.



# Sugestões

* Deixa a estrutura dos aquivos pronta no formato de um modulo para ser enviado a pypi, o projeto vais se chamar image-label-server

* Por falta estas variáveis estarão em
JSON_DB_DIR = "~/.config/image-label-server/json_data"
SQLITE_DB_DIR = "~/.config/image-label-server/sqlite_dbs"
JSON_USER_DIR = "~/.config/image-label-server/json_users"

* Lembra de criar e colocar todas as funções main dentro de      if __name__ == "__main__":

* server.py, client.py e export_csv.py pertencem ao modulo image-label-server
* Não faz sentido continuar com o servidor em server.py se:
    - Não há bases de dados no diretório SQLITE_DB_DIR, já que o servidor depende dessas bases para funcionar.
    - Não há usuários registrados no diretório JSON_USER_DIR, já que a autenticação é obrigatória para acessar os comandos.
