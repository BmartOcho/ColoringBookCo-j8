from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        prompts = {
            "comic-book": {
                "name": "Comic Book Style",
                "description": "Bold lines, stylized shadows, dynamic expressions"
            },
            "sketch": {
                "name": "Sketch Style", 
                "description": "Refined, hand-drawn pencil-like detailing"
            },
            "childrens-cartoon": {
                "name": "Children's Cartoon Style",
                "description": "Soft, rounded features and playful charm"
            },
            "basic-outline": {
                "name": "Photo Outline Style",
                "description": "Simplified black-and-white outline of the actual photo"
            },
            "caricature": {
                "name": "Caricature Style",
                "description": "Whimsical, bouncy line art with exaggerated character"
            }
        }
        
        self.wfile.write(json.dumps(prompts).encode())
