from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import requests
import json
import re
import urllib.parse

# Initialize the model and tokenizer (using a larger GPT-2 model)
model_name = "gpt2-medium"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# If you have a GPU and want to use it (only if CUDA is available)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

HIGH_RISK_KEYWORDS = ['hack', 'virus', 'attack', 'unauthorized', 'illegal', 'breach', 'exploit', 'steal', 'malware', 'phishing']

def get_ai_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=True).to(device)
    attention_mask = torch.ones(inputs.shape, device=device)
    outputs = model.generate(
        inputs, 
        max_length=200,
        num_return_sequences=1, 
        temperature=0.7,
        attention_mask=attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()

def check_and_update_ontology(agent_type, capability, tool, risk_level):
    url = "http://localhost:5001/ontology/check_and_update"
    data = {
        "agentType": agent_type,
        "capability": capability,
        "tool": tool,
        "riskLevel": risk_level
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the ontology server: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        return {"status": "error", "message": str(e)}

def parse_ai_output(ai_interpretation, user_input):
    # Try to parse using regex
    agent_type = re.search(r"Agent Type: (.+)", ai_interpretation)
    capability = re.search(r"Capability: (.+)", ai_interpretation)
    tool = re.search(r"Tool: (.+)", ai_interpretation)
    risk_level = re.search(r"Risk Level: (.+)", ai_interpretation)

    # Provide specific default values if parsing fails
    parsed_output = {
        "agent_type": agent_type.group(1) if agent_type else "Unknown Agent",
        "capability": capability.group(1) if capability else "Unknown Capability",
        "tool": tool.group(1) if tool else "Unknown Tool",
        "risk_level": risk_level.group(1) if risk_level else "Medium"
    }

    # Decode URL-encoded values
    for key, value in parsed_output.items():
        parsed_output[key] = urllib.parse.unquote(value)

    # Check for placeholder text
    placeholder_patterns = [r'\[.+?\]', r'\<.+?\>']
    for key, value in parsed_output.items():
        if any(re.search(pattern, value) for pattern in placeholder_patterns):
            parsed_output[key] = f"Unknown {key.capitalize()}"

    # Check for high-risk keywords in the user input and parsed output
    if any(keyword in user_input.lower() for keyword in HIGH_RISK_KEYWORDS) or \
       any(keyword in ' '.join(parsed_output.values()).lower() for keyword in HIGH_RISK_KEYWORDS):
        parsed_output["risk_level"] = "High"

    return parsed_output

def ai_agent_action(user_input):
    interpretation_prompt = f"""Analyze the following action and provide a structured response:
Action: {user_input}

You must respond using EXACTLY this format, replacing the text in brackets with your analysis:
Agent Type: [type of agent that would perform this action]
Capability: [main capability required for this action]
Tool: [specific tool or software used for this action]
Risk Level: [Low, Medium, or High]

Consider carefully the ethical and legal implications of the action when assigning the Risk Level.

Do not include any other text or explanation in your response. Only provide the four lines above with your analysis.

Your response:"""

    ai_interpretation = get_ai_response(interpretation_prompt)
    print("Raw AI Interpretation:", ai_interpretation)

    parsed_interpretation = parse_ai_output(ai_interpretation, user_input)
    print(f"Parsed Interpretation:\n{json.dumps(parsed_interpretation, indent=2)}")

    # Always set risk level to High if high-risk keywords are present
    if any(keyword in user_input.lower() for keyword in HIGH_RISK_KEYWORDS):
        parsed_interpretation['risk_level'] = 'High'
        print("High-risk keyword detected. Risk level set to High.")

    # Check and update ontology
    result = check_and_update_ontology(
        parsed_interpretation['agent_type'],
        parsed_interpretation['capability'],
        parsed_interpretation['tool'],
        parsed_interpretation['risk_level']
    )

    if result['status'] == 'danger' or parsed_interpretation['risk_level'] == 'High':
        return f"Cannot perform this action due to high risk. This action may be unsafe or unethical."
    elif result['status'] == 'error':
        return f"Error occurred: {result['message']}"
    else:
        action_response = "Action cannot be performed due to potential safety concerns."
        return f"Action interpretation:\n{json.dumps(parsed_interpretation, indent=2)}\n\nAction performed: {action_response}\n\nOntology update: {result['message']}"

# Example usage
if __name__ == "__main__":
    print("AI Agent initialized. Type 'quit' to exit.")
    while True:
        user_input = input("\nEnter an action for the AI agent to perform: ")
        if user_input.lower() == 'quit':
            break
        result = ai_agent_action(user_input)
        print(result)
        print("\n---\n")