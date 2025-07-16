from pyshacl import validate
import rdflib
import sys
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_shacl_validation(data_file, shapes_file):
    # Load the data graph
    data_graph = rdflib.Graph()
    data_graph.parse(data_file, format="turtle")
    logging.info(f"Data graph loaded with {len(data_graph)} triples.")

    # Load the SHACL shapes graph
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(shapes_file, format="turtle")
    logging.info(f"Shapes graph loaded with {len(shapes_graph)} triples.")

    # Perform SHACL validation
    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        debug=False
    )
    logging.info("Validation Results:")
    logging.info(results_text)
    
    if conforms:
        logging.info("The ontology conforms to the SHACL shapes.")
    else:
        logging.error("The ontology does not conform to the SHACL shapes.")
        logging.error("Results graph:")
        logging.error(results_graph.serialize(format='turtle'))
    
    return conforms


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <data_file> <shapes_file>")
        sys.exit(1)

    data_file = sys.argv[1]
    shapes_file = sys.argv[2]

    logging.info(f"Running SHACL validation on {data_file} with shapes {shapes_file}...")
    conforms = run_shacl_validation(data_file, shapes_file)
    sys.exit(0 if conforms else 1)