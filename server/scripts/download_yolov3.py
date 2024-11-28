import os
import requests

# Define the URLs for the weights and config files
urls = {
    "yolov3.weights": "https://pjreddie.com/media/files/yolov3.weights",
    "yolov3.cfg": "https://raw.githubusercontent.com/pjreddie/darknet/refs/heads/master/cfg/yolov3.cfg",
    "coco.names": "https://github.com/pjreddie/darknet/blob/master/data/coco.names?raw=true"
}

# Create a directory to store the downloaded files
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3"), exist_ok=True)

# Function to download a file
def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File {filename} already exists, skipping download")
        return
        
    print(f"Starting download of {filename} from {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get total file size if available
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        downloaded = 0

        with open(filename, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                
                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    print(f"Downloading {filename}: {percent}% ({downloaded}/{total_size} bytes)", end='\r')
                else:
                    print(f"Downloading {filename}: {downloaded} bytes downloaded", end='\r')
                    
        print(f"\nSuccessfully downloaded {filename} ({downloaded} bytes)")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {filename}: {str(e)}")

# Download each file
model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3")
for filename, url in urls.items():
    filepath = os.path.join(model_dir, filename)
    download_file(url, filepath)