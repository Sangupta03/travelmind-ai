import json
import os

MEMORY_FILE = "memory/user_profiles.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_profile(username):
    memory = load_memory()
    return memory.get(username, {})

def update_user_profile(username, new_data):
    memory = load_memory()

    if username not in memory:
        memory[username] = {}

    memory[username].update(new_data)
    save_memory(memory)
