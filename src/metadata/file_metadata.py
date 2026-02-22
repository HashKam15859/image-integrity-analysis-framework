import os
from PIL import Image

def extract_file_encoding_metadata(image_path):
	""" Extracts file-level encoding and compression metadata.
	This information reflects how the image is stored internally, 
	not what the metadata claims. """
	
	# Open image using Pillow
	img = Image.open(image_path)
	
	#-------------------------------
	# Basic file-level information
	#-------------------------------
	file_metadata = {
		"file_size_bytes": os.path.getsize(image_path), 
		"image_format": img.format, # JPEG, PNG, etc
		"image_mode": img.mode, 
		"mime_type": Image.MIME.get(img.format), 
		"compression": img.info.get("compression"),
		"bits_per_sample": None, 
		"color_components": None, 
		"chroma_subsampling": None
		}
		
	#----------------------------------
	# Bits per sample & color channels
	#----------------------------------
	if img.mode == "RGB": 
		file_metadata["bits_per_sample"] = 8
		file_metadata["color_components"] = 3
	elif img.mode == "RGBA":
		file_metadata["bits_per_sample"] = 8
		file_metadata["color_components"] = 4
	elif img.mode == "L":
		file_metadata["bits_per_sample"] = 8
		file_metadata["color_components"] = 1
	else: 
		# For uncommon modes, leave as unknown
		file_metadata["bits_per_sample"] = "Unknown"
		file_metadata["color_components"] = "Unknown"
		
	#-----------------------------------
	# JPEG-specific compression details
	#-----------------------------------
	if img.format == "JPEG":
		# Subsmapling info is stored in image info (if available)
		subsampling = img.info.get("subsampling")
		
		if subsampling == 0: 
			file_metadata["chroma_subsampling"] = "4:4:4"
		elif subsampling == 1: 
			file_metadata["chroma_subsampling"] = "4:2:2"
		elif subsampling == 2:
			file_metadata["chroma_subsampling"] = "4:2:0"
		else:
			file_metadata["chroma_subsampling"] = "Unknown"
			
	return file_metadata
