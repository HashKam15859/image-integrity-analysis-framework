from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS

def extract_exif_metadata(image_path):
	""" Extracts EXIF metadata from an image file.
	Returns a structured dictionary of relevant forensic metadata."""
	
	# Open the image using Pillow
	img = Image.open(image_path)
	exif_data = {}
	
	# JPEG EXIF handling
	if img.format == "JPEG":
		if hasattr(img, "_getexif"):
			exif = img._getexif()
			if exif:
				exif_data = exif
	# TIEF EXIF handling	
	elif img.format == "TIFF":
		if hasattr(img, "tag_v2"):
			for tag_id, value, in img.tag_v2.items():
				tag_name = ExifTags.TAGS.get(tag_id, tag_id)
				exif_data[tag_name] = value
				
	if not exif_data:
		return {
			"has_exif": False, 
			"camera_make": None, 
			"camera_model": None, 
			"datetime_original": None, 
			"software": None, 
			"gps_info": None
			}
	
	# Dictionary to store processed metadata
	metadata = {
		"has_exif": True,
		"camera_make": None, 
		"camera_model": None, 
		"datetime_original": None, 
		"software": None,
		"gps_info": None
		}
	# Iterate through raw EXIF tags
	for tag_id, value in exif_data.items():
		# Convert numeric EXIF tag IDs to readable names
		tag_name = TAGS.get(tag_id, tag_id)
		
		# Camera manufacturer
		if tag_name == "Make":
			metadata["camera_make"] = value
		
		# Camera model 
		elif tag_name == "Model": 
			metadata["camera_model"] = value
		
		# Date and time when image was originally captured
		elif tag_name == "DateTimeOriginal": 
			metadata["datetime_original"] = value
		
		# Software used to edit or process the image
		elif tag_name == "GPSInfo":
			metadata["gps_info"] = extract_gps_info(value)
			
	return metadata
	
def extract_gps_info(gps_data):
	""" Process raw GPS EXIF metadata and converts it into a readable dictionary format. """
	gps_info = {} 
	
	if not isinstance(gps_data, dict):
		return gps_info
	
	for key in gps_data:
		decoded_key = GPSTAGS.get(key, key)
		gps_info[decoded_key] = gps_data[key]
		
	return gps_info
	
