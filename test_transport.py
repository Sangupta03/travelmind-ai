from core.transport_engine import TransportEngine

engine = TransportEngine()

def print_decision(origin, destination):
    decision = engine.decide(origin, destination)

    print(f"\nRoute: {origin} → {destination}")
    print(f"Mode: {decision['mode']}")
    print(f"Distance: {decision['distance']}")
    print(f"Time: {decision['time']}")
    print(f"Reason: {decision['reason']}")


print_decision("City Palace Jaipur", "Jantar Mantar Jaipur")
print_decision("Hawa Mahal", "Amber Fort Jaipur")
