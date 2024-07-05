import random

def get_response(message: str) -> str:
    lowered = message.lower()

    if lowered == '':
        return "Well, you're awfully silent..."
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you!'
    elif 'roll dice' in lowered:
        return f'You rolled: {random.randint(1, 6)}'
    else:
        return random.choice(['I do not understand that.', 'Could you please rephrase?', 'I am not sure what you mean.'])
