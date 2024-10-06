from neo4j import GraphDatabase
from owlready2 import *
from pyvis.network import Network

# Load your ontology
ONTOLOGY_FILE = "agent-ontology.owx"  # Update this to match your ontology file name
onto = get_ontology(ONTOLOGY_FILE).load()

# Neo4j connection details
URI = "neo4j+s://e2417da5.databases.neo4j.io:7687"
AUTH = ("neo4j", "OKdzqtO8A24erkyg0y8gTHMEr60tu0UPSw8mwcYUiik") 

def connect_to_neo4j(uri, auth):
    return GraphDatabase.driver(uri, auth=auth)

def close_neo4j_connection(driver):
    driver.close()

def add_node(tx, label, properties):
    query = (
        f"MERGE (n:{label} {{name: $name}}) "
        f"SET n += $properties"
    )
    tx.run(query, name=properties['name'], properties=properties)

def add_relationship(tx, start_node, end_node, relationship_type, properties=None):
    query = (
        f"MATCH (a:{start_node['label']} {{name: $start_name}}), "
        f"(b:{end_node['label']} {{name: $end_name}}) "
        f"MERGE (a)-[r:{relationship_type}]->(b) "
        f"SET r += $properties"
    )
    tx.run(query, start_name=start_node['name'], end_name=end_node['name'], properties=properties or {})

def transfer_ontology_to_neo4j(driver, onto):
    with driver.session() as session:
        # Add classes as nodes
        for cls in onto.classes():
            session.write_transaction(add_node, "Class", {"name": cls.name})
        
        # Add individuals as nodes
        for individual in onto.individuals():
            session.write_transaction(add_node, "Individual", {"name": individual.name})
        
        # Add relationships
        for cls in onto.classes():
            for subclass in cls.subclasses():
                session.write_transaction(add_relationship, 
                                          {"label": "Class", "name": subclass.name},
                                          {"label": "Class", "name": cls.name},
                                          "IS_A")
            
            for individual in cls.instances():
                session.write_transaction(add_relationship,
                                          {"label": "Individual", "name": individual.name},
                                          {"label": "Class", "name": cls.name},
                                          "INSTANCE_OF")

def visualize_neo4j_data():
    driver = connect_to_neo4j(URI, AUTH)
    net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white")

    with driver.session() as session:
        # Query to get nodes with their labels and names
        result = session.run("MATCH (n) RETURN id(n) AS id, labels(n) AS labels, n.name AS name")
        for record in result:
            node_id = record['id']
            labels = record['labels']
            name = record['name']
            label = f"{labels[0]}: {name}" if name else labels[0]
            net.add_node(node_id, label=label, title=label, group=labels[0])

        # Query to get relationships
        result = session.run("MATCH (a)-[r]->(b) RETURN id(a) AS source, id(b) AS target, type(r) AS type")
        for record in result:
            net.add_edge(record['source'], record['target'], title=record['type'])

    close_neo4j_connection(driver)
    net.show_buttons(filter_=['physics'])
    net.show("ontology_visualization.html")

def update_neo4j():
    driver = connect_to_neo4j(URI, AUTH)
    transfer_ontology_to_neo4j(driver, onto)
    close_neo4j_connection(driver)

if __name__ == "__main__":
    update_neo4j()
    visualize_neo4j_data()