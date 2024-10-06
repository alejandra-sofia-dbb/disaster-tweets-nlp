from flask import Flask, request, jsonify
from flask_cors import CORS
from owlready2 import *
import os
import logging
from neo4j_integration import update_neo4j

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Path to your ontology file
ONTOLOGY_FILE = "agent-ontology.owx"

# Load the existing ontology or create a new one if it doesn't exist
if os.path.exists(ONTOLOGY_FILE):
    ontology = get_ontology(ONTOLOGY_FILE).load()
else:
    ontology = get_ontology("http://example.org/agent-ontology#")

# Define object properties if they don't exist
with ontology:
    if "hasCapability" not in ontology.object_properties():
        class hasCapability(ObjectProperty):
            domain = [Thing]
            range = [Thing]
    
    if "usesTool" not in ontology.object_properties():
        class usesTool(ObjectProperty):
            domain = [Thing]
            range = [Thing]
    
    if "hasRiskLevel" not in ontology.object_properties():
        class hasRiskLevel(ObjectProperty):
            domain = [Thing]
            range = [Thing]

@app.route('/ontology/check_and_update', methods=['POST'])
def check_and_update():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
        
        agent_type = data.get('agentType')
        capability = data.get('capability')
        tool = data.get('tool')
        risk_level = data.get('riskLevel')

        if not all([agent_type, capability, tool, risk_level]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        with ontology:
            # Find or create classes
            agent_class = types.new_class(agent_type, (Thing,))
            capability_class = types.new_class(capability, (Thing,))
            tool_class = types.new_class(tool, (Thing,))
            risk_class = types.new_class(risk_level.replace(" ", ""), (Thing,))

            # Find or create instance
            instance_name = f"{agent_type.lower()}_instance"
            agent_instance = agent_class(instance_name)

            # Update properties
            if not hasattr(agent_instance, 'hasCapability'):
                agent_instance.hasCapability = []
            if capability_class not in agent_instance.hasCapability:
                agent_instance.hasCapability.append(capability_class)
            
            if not hasattr(agent_instance, 'usesTool'):
                agent_instance.usesTool = []
            if tool_class not in agent_instance.usesTool:
                agent_instance.usesTool.append(tool_class)
            
            if not hasattr(agent_instance, 'hasRiskLevel'):
                agent_instance.hasRiskLevel = []
            if risk_class not in agent_instance.hasRiskLevel:
                agent_instance.hasRiskLevel = [risk_class]  # Assuming one risk level at a time

            # Check risk level - now more conservative
            is_high_risk = any("high" in str(risk).lower() for risk in agent_instance.hasRiskLevel) or \
                           risk_level.lower() == 'high' or \
                           any(keyword in f"{agent_type} {capability} {tool}".lower() for keyword in ['hack', 'virus', 'attack', 'unauthorized', 'illegal', 'breach', 'exploit', 'steal', 'malware', 'phishing'])

        # Save changes to the ontology file
        ontology.save(file=ONTOLOGY_FILE)
        update_neo4j()


        if is_high_risk:
            return jsonify({
                "status": "danger",
                "message": "This action is too risky. Human intervention required."
            }), 403
        else:
            return jsonify({
                "status": "caution",
                "message": "Action may have potential risks. Proceed with caution."
            }), 200

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)