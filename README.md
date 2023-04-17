# Proyecto de Sistemas Distribuidos


**Autores: C411 - Harold Rosales Hernandez C411 - Oscar Luis Hernadez Solano**



## Modo de uso

python3 client.py client-ip client-port bootstrap-routing-node-ip bootstrap-routing-port

• add -f file-list -t tag-list

Copia uno o más ficheros hacia el sistema y estos son inscritos con
las etiquetas contenidas en tag-list.

• delete -q tag-query

Elimina todos los ficheros que cumplan con la consulta tag-query.

• list -q tag-query

Lista el nombre y las etiquetas de todos los ficheros que cumplan con
la consulta tag-query.

• add-tags -q tag-query -t tag-list

Añade las etiquetas contenidas en tag-list a todos los ficheros que
cumpan con la consulta tag-query.

• delete-tags -q tag-query -t tag-list

Elimina las etiquetas contenidas en tag-list de todos los ficheros que
cumplan con la consulta tag-query.

• get -q tag-query

Descarga todos los ficheros que cumplan con
la consulta tag-query. Los ficheros seran almacenados en la carpeta 'downloads' del Proyecto.

### Inicializar la red

Iniciar:


python3 first_node.py bootstrap-routing-node-ip bootstrap-routing-port



## Practical Use Example
1. Start a new network 
    ```
    python3 start_network.py
    ```

2. Start talking to a node member of that network created above, and send some files
    ```
    python3 client.py 127.0.0.1 8000 127.0.0.1 9000
    ```

3. Send a file
    ```
    python3 add -f foto_test.jpg -t f1
    ```

4. Check the image we just uploaded to the system 
    ```
    python3 list -q f1
    ```

5. In theory the file `f1` should'nt be just on the node `127.0.0.1:9000`, it should be distributed on the network. So if if the node went down, we still should be able to recover the file. Let's try do that

6. Kill the node
    ```
    kill -9 127.0.0.1 9000
    ```

7. Recover the file
    ```
    python3 list -q f1
    ```

8. File should be listed, with a warning that the connection to the previous node has been lost