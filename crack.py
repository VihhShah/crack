import os
import shutil
import json
import requests
import cv2
from PIL import Image, ImageDraw
import numpy as np
import csv

API_URL = "https://outline.roboflow.com"
API_KEY = "5KXaL3rsDpNDVSwX6ZZB"
MODEL_ID = "crack-btlnb/4"

dataset_folder_path = 'Task_11/positive'
labeled_folder_path = os.getcwd() + '/bridge_crack/assets/labeled_dataset'
without_crack_folder_path = os.getcwd() + '/bridge_crack/assets/without_bridge_crack_dataset'
csv_file_path = os.getcwd() + '/bridge_crack/cr_data.csv'

# Actual reference object dimensions in meters
actual_length_meters = 1.0  # 1 meter
actual_width_meters = 0.5  # 0.5 meters
actual_area_meters = actual_length_meters * actual_width_meters  # 0.5 square meters

# Reference object dimensions in pixels
length_pixels = 100  # 100 pixels
width_pixels = 50  # 50 pixels
pixel_area = length_pixels * width_pixels  # 5000 square pixels

# Calculate conversion factor from pixels to meters
PIXELS_TO_METERS_CONVERSION_FACTOR = (actual_area_meters / pixel_area) ** 0.5
print(f"Conversion Factor: {PIXELS_TO_METERS_CONVERSION_FACTOR} meters per pixel")

def clean_folders():
    """Clean and create necessary folders."""
    for folder in [labeled_folder_path, without_crack_folder_path]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

def contour_from_api(image_path):
    """Get contours from API."""
    url = f"{API_URL}/{MODEL_ID}?api_key={API_KEY}"
    with open(image_path, 'rb') as image_file:
        files = {"file": image_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.json().get('error', 'Unknown error')}")
        return None

def draw_contours(image_path, contours):
    """Draw contours on the image."""
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    for contour in contours:
        points = contour.get('points', [])
        for point in points:
            x, y = point.get('x'), point.get('y')
            if x is not None and y is not None:
                draw.ellipse((x-5, y-5, x+5, y+5), fill='green', outline='green')
    
    return image

def calculate_contour_area(contours):
    """Calculate the total contour area in pixels."""
    total_area = 0
    for contour in contours:
        points = [(point['x'], point['y']) for point in contour.get('points', [])]
        if len(points) >= 3:
            cnt = np.array(points, dtype=np.int32)
            area = cv2.contourArea(cnt)
            total_area += area
    return total_area


def main():
    """Main function to clean folders, process images, and save results to CSV."""
    # Step 1: Clean and prepare folders
    clean_folders()

    # Step 2: Open CSV for writing results
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Image Name", "Crack Detected"])  # No actual crack area

        # Step 3: Process each image in the dataset
        for filename in os.listdir(dataset_folder_path):
            image_path = os.path.join(dataset_folder_path, filename)
            if os.path.isfile(image_path):
                response = contour_from_api(image_path)

                if response:
                    contours = response.get('predictions', [])
                    if contours:
                        # Write result to CSV (Crack Detected: Yes)
                        writer.writerow([filename, "Yes"])

                        # Draw and save labeled image
                        labeled_image = draw_contours(image_path, contours)
                        labeled_image.save(os.path.join(labeled_folder_path, filename))
                    else:
                        # Write result to CSV (Crack Detected: No)
                        writer.writerow([filename, "No"])

                        # Copy images without cracks
                        shutil.copy(image_path, os.path.join(without_crack_folder_path, filename))

    print("Processing complete. Results saved.")

# Run the main function
if __name__ == "__main__":
    def main():
    
        clean_folders()

    # Step 2: Open CSV for writing results
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Image Name", "Crack Detected"])

        # Step 3: Process each image in the dataset
        for filename in os.listdir(dataset_folder_path):
            image_path = os.path.join(dataset_folder_path, filename)
            if os.path.isfile(image_path):
                response = contour_from_api(image_path)

                if response:
                    contours = response.get('predictions', [])
                    if contours:
                        # Write result to CSV (Crack Detected: Yes)
                        writer.writerow([filename, "Yes"])

                        
                    else:
                        # Write result to CSV (Crack Detected: No)
                        writer.writerow([filename, "No"])

                        # Copy images without cracks
                        shutil.copy(image_path, os.path.join(without_crack_folder_path, filename))

    print("Processing complete. Results saved.")

