from http.server import BaseHTTPRequestHandler
import json
import cgi
import io
import os
import base64
import requests
import zipfile
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # Check if OpenAI API key is available
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if not openai_api_key:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': 'OpenAI API key not configured'}
                self.wfile.write(json.dumps(error_response).encode())
                return

            # Define the 5 available prompts
            AVAILABLE_PROMPTS = {
                "comic-book": "Use the reference image to create a black and white image for a coloring book in this style: Comic Book Style – Bold lines, stylized shadows, dynamic expressions",
                "sketch": "Use the reference image to create a black and white image for a coloring book in this style: Sketch Style – Refined, hand-drawn pencil-like detailing",
                "childrens-cartoon": "Use the reference image to create a black and white image for a coloring book in this style: Children's Cartoon Style – Soft, rounded features and playful charm",
                "basic-outline": "Use the reference image to create a black and white image for a coloring book in this style: Photo Outline Style – Simplified black-and-white outline of the actual photo",
                "caricature": "Use the reference image to create a black and white image for a coloring book in this style: Caricature Style – Whimsical, bouncy line art with exaggerated character"
            }

            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': 'Content-Type must be multipart/form-data'}
                self.wfile.write(json.dumps(error_response).encode())
                return

            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse form data
            form = cgi.FieldStorage(
                fp=io.BytesIO(post_data),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Get selected prompt
            prompt_field = form.getvalue('prompt')
            if not prompt_field or prompt_field not in AVAILABLE_PROMPTS:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': f'Invalid or missing prompt. Available options: {", ".join(AVAILABLE_PROMPTS.keys())}'}
                self.wfile.write(json.dumps(error_response).encode())
                return

            selected_prompt = AVAILABLE_PROMPTS[prompt_field]

            # Get uploaded images
            if 'images' not in form:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': 'No images provided'}
                self.wfile.write(json.dumps(error_response).encode())
                return

            images = form['images']
            if not isinstance(images, list):
                images = [images]

            processed_images = []
            
            for i, image_field in enumerate(images):
                if image_field.file:
                    try:
                        # Read and encode the image
                        image_data = image_field.file.read()
                        base64_image = base64.b64encode(image_data).decode('utf-8')
                        
                        # Determine image format
                        content_type = image_field.type or 'image/jpeg'
                        if 'jpeg' in content_type:
                            image_format = 'jpeg'
                        elif 'png' in content_type:
                            image_format = 'png'
                        elif 'webp' in content_type:
                            image_format = 'webp'
                        else:
                            image_format = 'jpeg'

                        # Call OpenAI API
                        headers = {
                            'Authorization': f'Bearer {openai_api_key}',
                            'Content-Type': 'application/json'
                        }

                        payload = {
                            'model': 'gpt-image-1',
                            'prompt': selected_prompt,
                            'image': f'data:image/{image_format};base64,{base64_image}',
                            'size': '1024x1024',
                            'quality': 'standard',
                            'response_format': 'url',
                            'n': 1
                        }

                        response = requests.post(
                            'https://api.openai.com/v1/images/generations',
                            headers=headers,
                            json=payload,
                            timeout=60
                        )

                        if response.status_code == 200:
                            response_data = response.json()
                            generated_image_url = response_data['data'][0]['url']

                            # Download the generated image
                            img_response = requests.get(generated_image_url, timeout=30)
                            if img_response.status_code == 200:
                                filename = f'{prompt_field}_{image_field.filename or f"image_{i+1}"}_{i+1}.png'
                                processed_images.append({
                                    'filename': filename,
                                    'data': img_response.content
                                })

                    except Exception as e:
                        print(f"Error processing image {i+1}: {str(e)}")
                        continue

            if not processed_images:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': 'No images could be processed successfully'}
                self.wfile.write(json.dumps(error_response).encode())
                return

            # Create zip file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for img in processed_images:
                    zip_file.writestr(img['filename'], img['data'])
            
            zip_buffer.seek(0)
            zip_data = zip_buffer.getvalue()

            # Return the zip file
            self.send_header('Content-type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="ColoringBook_{prompt_field.replace("-", "_")}.zip"')
            self.send_header('Content-Length', str(len(zip_data)))
            self.end_headers()
            self.wfile.write(zip_data)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'error': f'Internal server error: {str(e)}'}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
