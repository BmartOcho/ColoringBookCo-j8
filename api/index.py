from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import base64
import zipfile
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, origins="*")  # Enable CORS for all origins

@app.route('/api/process-images', methods=['POST'])
def process_images():
    try:
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500

        # Define the 5 available prompts based on your specifications
        AVAILABLE_PROMPTS = {
            "comic-book": "Use the reference image to create a black and white image for a coloring book in this style: Comic Book Style – Bold lines, stylized shadows, dynamic expressions",
            "sketch": "Use the reference image to create a black and white image for a coloring book in this style: Sketch Style – Refined, hand-drawn pencil-like detailing",
            "childrens-cartoon": "Use the reference image to create a black and white image for a coloring book in this style: Children's Cartoon Style – Soft, rounded features and playful charm",
            "basic-outline": "Use the reference image to create a black and white image for a coloring book in this style: Photo Outline Style – Simplified black-and-white outline of the actual photo",
            "caricature": "Use the reference image to create a black and white image for a coloring book in this style: Caricature Style – Whimsical, bouncy line art with exaggerated character"
        }

        # Get the selected prompt from form data
        selected_prompt_key = request.form.get('prompt')
        if not selected_prompt_key:
            return jsonify({'error': 'No prompt selected. Please choose one of: comic-book, sketch, childrens-cartoon, basic-outline, caricature'}), 400

        if selected_prompt_key not in AVAILABLE_PROMPTS:
            return jsonify({'error': f'Invalid prompt selected. Available options: {", ".join(AVAILABLE_PROMPTS.keys())}'}), 400

        selected_prompt = AVAILABLE_PROMPTS[selected_prompt_key]

        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400

        files = request.files.getlist('images')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No images selected'}), 400

        # Process each image
        processed_images = []
        
        for i, file in enumerate(files):
            if file and file.filename:
                try:
                    # Read and encode the image
                    image_data = file.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    
                    # Call OpenAI API using gpt-image-1 model
                    headers = {
                        'Authorization': f'Bearer {openai_api_key}',
                        'Content-Type': 'application/json'
                    }

                    # Determine the image format for the data URL
                    content_type = file.content_type
                    if content_type == 'image/jpeg':
                        image_format = 'jpeg'
                    elif content_type == 'image/png':
                        image_format = 'png'
                    elif content_type == 'image/webp':
                        image_format = 'webp'
                    else:
                        # Default to jpeg if format is unclear
                        image_format = 'jpeg'

                    # Use gpt-image-1 model for image generation with selected prompt
                    payload = {
                        'model': 'gpt-image-1',
                        'prompt': selected_prompt,
                        'image': f'data:image/{image_format};base64,{base64_image}',
                        'size': '1024x1024',
                        'quality': 'standard',
                        'response_format': 'url',
                        'n': 1
                    }

                    # Make the API call to OpenAI's image generation endpoint
                    response = requests.post(
                        'https://api.openai.com/v1/images/generations',
                        headers=headers,
                        json=payload,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f"OpenAI API error for image {i+1}: {response.text}")
                        continue

                    response_data = response.json()
                    generated_image_url = response_data['data'][0]['url']

                    # Download the generated image
                    img_response = requests.get(generated_image_url, timeout=30)
                    if img_response.status_code == 200:
                        original_filename = secure_filename(file.filename)
                        name_without_ext = os.path.splitext(original_filename)[0]
                        # Include the style in the filename for clarity
                        processed_images.append({
                            'filename': f'{selected_prompt_key}_{name_without_ext}_{i+1}.png',
                            'data': img_response.content
                        })
                    else:
                        print(f"Failed to download generated image {i+1}")
                        
                except Exception as e:
                    print(f"Error processing image {i+1}: {str(e)}")
                    continue
        
        if not processed_images:
            return jsonify({'error': 'No images could be processed successfully'}), 500
        
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img in processed_images:
                zip_file.writestr(img['filename'], img['data'])
        
        zip_buffer.seek(0)
        
        # Return the zip file with style-specific naming
        zip_filename = f'ColoringBook_{selected_prompt_key.replace("-", "_")}.zip'
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/prompts', methods=['GET'])
def get_available_prompts():
    """Endpoint to get all available prompt options"""
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
    return jsonify(prompts)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Image processing API is running'})

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
