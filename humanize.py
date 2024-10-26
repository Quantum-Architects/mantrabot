"""{'events': [{'type': 'message', 'attributes': [{'key': 'action', 'value': '/cosmos.bank.v1beta1.MsgSend', 'index': True}, {'key': 'sender', 'value': 'mantra1nagtgts4y4s3d08ykqe0vsd68l53gnlujms9zj', 'index': True}, {'key': 'module', 'value': 'bank', 'index': True}, {'key': 'msg_index', 'value': '0', 'index': True}]}]}""" # noqa: E501


def event(data, wallet):
    output = []

    # Extract and format general information
    output.append(f"Query: {data.get('query', 'N/A')}")

    # Process each event generically
    for event in data.get('events', []):
        event_type = event.get('type', 'Unknown')
        output.append(f'Event Type: {event_type.capitalize()}')

        # We only care about transfer
        if event_type.capitalize() == 'Transfer':
            is_sender = True
            sender = ''
            receiver = ''
            amount = 0
            is_valid = True
            # Process each attribute in the event
            for attr in event.get('attributes', []):
                key = attr.get('key', 'Unknown').replace('_', ' ').capitalize()
                value = attr.get('value', 'N/A')
                if value == 'mantra13pxn9n3qw79e03844rdadagmg0nshmwf4txc8r':
                    # Ingnore the fee module account
                    is_valid = False
                    continue

                if value == wallet:
                    # This is the user wallet
                    if key == 'Recipient':
                        is_sender = False

                if key == 'Recipient':
                    receiver = value
                if key == 'Sender':
                    sender = value

                if key == 'Amount':
                    amount = value

                # # Special case for action key to extract transaction type if present
                # if key.lower() == 'action' and '.' in value:
                #     transaction_type = value.split('.')[-1]
                #     output.append(f" - Transaction Type: {transaction_type}")
                # else:
                #     output.append(f" - {key}: {value}")
            if is_valid:
                if is_sender:
                    return ( f"""📫 MantraBot Notification 📫

💸 You sent {amount} to {receiver} 💸""")
                else:
                    return (f"""📫 MantraBot Notification 📫

🤑 You got {amount} from {sender} 🤑""")
            output.append('')  # Add a line break between events

    return '\n'.join(output)
