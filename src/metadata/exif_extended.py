from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

def extract_extended_exif(image_path):
	""" Extracts extended EXIF metadata related to camera capture settings.
	These fields are useful for forensics analysis of image origin and 
	post-capture modification. """
	
	# Open the iamge file
	img = Image.open(image_path)
	exif_data = {}
	
	# JPEG Handling
	if img.format == "JPEG":
		if hasattr(img, "_getexif"):
			exif = img._getexif()
			if exif: 
				exif_data = exif
	
	# TIFF handling
	elif img.format == "TIFF":
		if hasattr(img, "tag_v2"):
			for tag_id, value in img.tag_v2.items():
				exif_data[tag_id] = value
	
	# Dictionary to store extended capture-related metadata
	extended_metadata = {
		"has_extended_exif": True, 
		"exposure_time": None, 
		"f_number": None, 
		"iso_speed": None, 
		"focal_length": None, 
		"flash": None, 
		"white_balance": None,
		"metering_mode": None
		}
	# Iterate through EXIF tags
	for tag_id, value in exif_data.items(): 
		# Convert numeric tag ID to readable tag name
		tag_name = TAGS.get(tag_id, tag_id)
		
		# Exposure time (e.g., 1/125 sec)
		if tag_name == "ExposureTime":
			extended_metadata["exposure_time"] = value
		
		# Aperture value (F-number)
		elif tag_name == "FNumber":
			extended_metadata["f_number"] = value
		
		# ISO snesitivity
		elif tag_name == "ISOSpeedRatings":
			extended_metadata["iso_speed"] = value
		
		# Focal length of the lens
		elif tag_name == "FocalLength":
			extended_metadata["focal_length"] = value	
		
		#Flash usage (whether flash fired)
		elif tag_name == "Flash": 
			extended_metadata["flash"] = value
			
		# White balance mode (auto/manual)
		elif tag_name == "WhiteBalance":
			extended_metadata["white_balance"] = value
			
		# Metering mode used by the camera
		elif tag_name == "MeteringMode":
			extended_metadata["metering_mode"] = value
			
	return extended_metadata
