""" Feature Vector Builder for AI-Assisted Image Forensics
This module converts the forensic analysis outputs into a numerical feature vector suitable for machine learning models. """

import numpy as np

def safe_numeric(value, default=0.0): 
	""" Safely converts a value to float. 
	Returns a default value if the input is None, NaN, or non-numeric. """
	try: 
		if value is None: 
			return default
		value = float(value)
		if np.isnan(value):
			return default
		return value
	except Exception: 
		return default
		
def build_feature_vector(
	exif_info, 
	metadata_analysis, 
	file_encoding, 
	content_analysis, 
	steg_analysis, 
	rule_based_score
	):
	""" Builds a fixed-length numerical feature vector for AI analysis. 
	Feature order (LOCKED):
	1. metadata_risk_score
	2. exif_score
	3. editing_software_detected
	4. is_jpeg
	5. jpeg_lossy_subsampling
	6. compression_present
	7. noise_variance
	8. edge_density
	9. texture_variance
	10. entropy
	11. lsb_variance
	12. steganalysis_score
	13. rule_based_score """
	
	#--------------------------
	# Metadata-based Features
	#--------------------------
	metadata_risk_score = safe_numeric(metadata_analysis.get("risk_score"), 0)
	has_exif = 1 if exif_info.get("has_exif") else 0
	editing_software_detected = (1 if exif_info.get("software") else 0)
	
	#-----------------------------
	# File Encoding & Compression
	#-----------------------------
	is_jpeg = 1 if file_encoding.get("image_format") == "JPEG" else 0
	
	# Encode JPEG chroma subsampling as ordinal values
	subsampling = file_encoding.get("chroma_subsampling")
	if subsampling == "4:2:0":
		jpeg_lossy_subsampling = 1
	elif subsampling == "4:2:2": 
		jpeg_lossy_subsampling = 2
	else: 
		jpeg_lossy_subsampling = 0
		
	compression_present = (1 if file_encoding.get("compression") else 0)
	
	#----------------------------
	# Content Forensics Features
	#----------------------------
	noise_variance = safe_numeric(content_analysis.get("noise_variance"), 0)
	edge_density = safe_numeric(content_analysis.get("edge_density"), 0)
	texture_variance = safe_numeric(content_analysis.get("texture_variance"), 0)
	
	#-----------------------
	# Steganalysis Features
	#-----------------------
	entropy = safe_numeric(steg_analysis.get("entropy"), 0)
	lsb_variance = safe_numeric(steg_analysis.get("lsb_variance"), 0)
	steganalysis_score = safe_numeric(steg_analysis.get("score"), 0)
	
	#----------------------------
	# Rule-based Summary Feature
	#----------------------------
	rule_based_score = safe_numeric(rule_based_score, 0)
	
	#----------------------
	# Final Feature Vector
	#----------------------
	feature_vector = np.array([
		metadata_risk_score,
		has_exif,
		editing_software_detected,
		is_jpeg,
		jpeg_lossy_subsampling, 
		compression_present, 
		noise_variance, 
		edge_density, 
		texture_variance,
		entropy,
		lsb_variance,
		steganalysis_score,
		rule_based_score
		], dtype=float)
	return feature_vector
