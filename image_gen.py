import os
from PIL import Image
import io
import requests
import urllib.parse
import random

def get_pexels_image(query):
    """
    Fetches a high quality image from Pexels API based on query.
    If no API Key is found, uses a high-quality "Mock" dictionary to simulate the API.
    """
    api_key = os.environ.get("PEXELS_API_KEY")
    
    # --- MOCK DATA FOR DEMO WITHOUT KEY ---
    # Top quality Pexels image URLs for common business/tech keywords
    MOCK_IMAGES = {
        "ai": "https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg", # Robot/AI
        "technology": "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg", # Tech code
        "business": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg", # Meeting
        "meeting": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg", # Meeting
        "construction": "https://images.pexels.com/photos/1216589/pexels-photo-1216589.jpeg", # Construction
        "building": "https://images.pexels.com/photos/1216589/pexels-photo-1216589.jpeg", # Building
        "office": "https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg", # Office laptop
        "data": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg", # Data graph
        "computer": "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg",
        "default": "https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg" # Safe fallback
    }

    if not api_key:
        print("PEXELS_API_KEY not found. Using MOCK data for demo.")
        # Simple keyword matching
        query_lower = query.lower()
        image_url = MOCK_IMAGES["default"]
        
        for key in MOCK_IMAGES:
            if key in query_lower:
                image_url = MOCK_IMAGES[key]
                print(f"Mock match found for '{key}': {image_url}")
                break
        
        try:
            img_response = requests.get(image_url, timeout=10)
            if img_response.status_code == 200:
                return Image.open(io.BytesIO(img_response.content))
        except Exception as e:
            print(f"Mock fetch failed: {e}")
            return get_fallback_image(query)
        
    try:
        headers = {
            "Authorization": api_key
        }
        # Search for 1 landscape photo, large size
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=1&orientation=landscape"
        
        print(f"Searching Pexels for: {query}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['photos']:
                # Get 'large' or 'original' image URL
                image_url = data['photos'][0]['src']['large2x'] # good quality
                print(f"Found Pexels Image: {image_url}")
                
                # Download image
                img_response = requests.get(image_url, timeout=15)
                if img_response.status_code == 200:
                    return Image.open(io.BytesIO(img_response.content))
            else:
                print("No photos found on Pexels.")
        else:
             print(f"Pexels API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Pexels search failed: {e}")

    # Fallback if Pexels fails
    return get_fallback_image(query)

def get_fallback_image(prompt):
    """
    Tries Picsum as a guaranteed fallback.
    """
    try:
        # Use a random seed based on prompt to get consistent random results per slide
        seed = len(prompt) + random.randint(0, 1000)
        url = f"https://picsum.photos/seed/{seed}/1920/1080"
        print(f"Trying Picsum Fallback: {url}")
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"Picsum fallback failed: {e}")

    # Absolute Last Resort
    return Image.new('RGB', (1920, 1080), color=(50, 50, 50))

def generate_background_image(prompt_en):
    """
    Main entry point. Now uses Pexels instead of Gemini.
    Arg name is kept as 'prompt_en' for compatibility, but treated as search keywords.
    """
    # Simply redirect to Pexels search
    # We might want to clean keywords slightly (remove 'high quality', 'cinematic', etc if Gemini adds them)
    # But usually Pexels handles them fine.
    return get_pexels_image(prompt_en)
