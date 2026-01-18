from tools.route_links import RouteLinkGenerator

gen = RouteLinkGenerator()

print(gen.generate("City Palace Jaipur", "Jantar Mantar Jaipur", "walking"))
print(gen.generate("Hawa Mahal", "Amber Fort Jaipur", "driving"))
