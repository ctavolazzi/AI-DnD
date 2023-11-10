config = {
    'modules': {
        'combat': {'option1': 'value1', 'option2': 'value2'},
        'dialogue': {'option1': 'value1', 'option2': 'value2'},
        # ... other modules
    },
    # ... other configuration options
    'locations': [
        {'name': 'Elenor',
         'description': 'You are in a quiet village surrounded by rolling hills.',
         'connections': {'north': 'forest'}},
        {'name': 'forest',
         'description': 'You are in a dark, dense forest. The trees obscure the sky.',
         'connections': {'south': 'Elenor'}},
    ]
}
