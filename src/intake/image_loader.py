import os
from PIL import Image
import hashlib

# List of image formats supported by the forensic tool
# Keeping this limited avoids unreliable analysis on rare formats
SUPPORTED_FORMATS = ["JPEG", "PNG", "TIFF", "BMP", "WEBP"]


def calculate_hash(image_path):
	""" Computes the SHA-256 hash of the image file. 
	This is used to verify the file integrity and support
	forensic chain-of-custody principles. """
	sha256 = hashlib.sha256()
	
	# Read the file in fixed-size blocks to handle large filse safely
	with open(image_path, "rb") as f:
		for block in iter(lambda: f.read(4096), b""):
			sha256.update(block)
			
	return sha256.hexdigest()


def load_image(image_path):
	""" This function performs the initial forensic intake of an image.
	It validates the image, extracts basic properties, and computes a
	cryptographic hash for integrity verification. """
	 
	if not os.path.exists(image_path):	# Check if the file path actually exists
		raise FileNotFoundError("Image file doesn't exist")
		
	try:
		img = Image.open(image_path) # Attempt to open the image using Pillow. This helps detect invalid or unsupported image files
		
		img.verify() # V erify checks for file corruption. It doesn NOT load image data fully, only validates structure
		
		img = Image.open(image_path) # Reopen the image after verification (verify() closes the file internally)
		
	except Exception: 
		raise ValueError("Invalid or corrupted image file:") # Any failure here means the image is invalid or corrupted
	
	if img.format not in SUPPORTED_FORMATS:		# Check whether the image format is supported
		raise ValueError(f"Unsupported iamge format: (img.format)")
	
	# Extract the basic forensic properties
	width, height = img.size # Image resolution
	mode = img.mode # Color encoding (RGB, L, etc)
	file_size = os.path.getsize(image_path) # Size in bytes
	
	# Generate cryptographic hash for integrity verification
	sha256_hash = calculate_hash(image_path)
	
	# Return all collected information as a structured dictionary
	return {
		"file_name": os.path.basename(image_path),
		"format": img.format, 
		"dimensions": f"{width} x {height}", 
		"color_mode": mode, 
		"file_size_bytes": file_size, 
		"sha256": sha256_hash,
		}	
