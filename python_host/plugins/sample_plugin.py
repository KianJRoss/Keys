"""
Sample Plugin for Keychron Menu System
"""

def get_commands():
    """Return a list of commands to register"""
    return [
        {
            "name": "Hello World",
            "description": "Prints hello to console",
            "callback": lambda: print("Hello from Plugin!")
        }
    ]
