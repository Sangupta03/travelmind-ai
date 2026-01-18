import urllib.parse

class RouteLinkGenerator:
    def generate(self, origin, destination, mode="driving"):
        origin_encoded = urllib.parse.quote(origin)
        dest_encoded = urllib.parse.quote(destination)

        return (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={origin_encoded}"
            f"&destination={dest_encoded}"
            f"&travelmode={mode}"
        )
