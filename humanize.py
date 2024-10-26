"""{'events': [{'type': 'message', 'attributes': [{'key': 'action', 'value': '/cosmos.bank.v1beta1.MsgSend', 'index': True}, {'key': 'sender', 'value': 'mantra1nagtgts4y4s3d08ykqe0vsd68l53gnlujms9zj', 'index': True}, {'key': 'module', 'value': 'bank', 'index': True}, {'key': 'msg_index', 'value': '0', 'index': True}]}]}"""

def humanize_event(data):
    output = []

    # Extract and format general information
    output.append(f"Query: {data.get('query', 'N/A')}")
    
    # Process each event generically
    for event in data.get('events', []):
        event_type = event.get('type', 'Unknown')
        output.append(f"Event Type: {event_type.capitalize()}")
        
        # Process each attribute in the event
        for attr in event.get('attributes', []):
            key = attr.get('key', 'Unknown').replace('_', ' ').capitalize()
            value = attr.get('value', 'N/A')
            
            # Special case for action key to extract transaction type if present
            if key.lower() == 'action' and '.' in value:
                transaction_type = value.split('.')[-1]
                output.append(f" - Transaction Type: {transaction_type}")
            else:
                output.append(f" - {key}: {value}")
        output.append("")  # Add a line break between events

    return "\n".join(output)