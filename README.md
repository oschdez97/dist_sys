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

Descarga todos los ficheros que cumplan con
la consulta tag-query.

• add-tags -q tag-query -t tag-list

Añade las etiquetas contenidas en tag-list a todos los ficheros que
cumpan con la consulta tag-query.

• delete-tags -q tag-query -t tag-list

Elimina las etiquetas contenidas en tag-list de todos los ficheros que
cumplan con la consulta tag-query.

## Inicializar la red

Iniciar:


python3 first_node.py bootstrap-routing-node-ip bootstrap-routing-port



