# Optimization
This program pulls json from url and then converts it to appropriate cypher queries. This program is part of the project for
database system course and is used in conjunction with Neo4J database.
#Examples
In order to use it you need to have selenium library installed or you can comment out code that uses selenium.

    $python extractNodes.py -store_id MTR //it is going to get all store ids of MTR and save them in a file
    $python extractNodes.py -load_pub MTR //uses id file; gets all publications; formats them in cypher query and saves unique pubId in a file
    $python extractNodes.py -load_store_info MTR //gets all store info and formats it into cypher query
    $python extractNodes.py -load_products MTR //uses unique pubId file, gets products and formats them in cypher query
    $python extractNodes.py -store_id -load_pub -load_store_info -load_products MTR
