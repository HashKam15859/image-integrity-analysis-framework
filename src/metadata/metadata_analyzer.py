def analyze_metadata_consistency(basic_exif, extended_exif):
	""" Analyzes consistency between basic and extended EXIF metadata.
	Produces forensic indicators related to provenance and editing
	"""
	
	indicators = []
	risk_score = 0 # simple cumulative score for metadata risk
	
	#-------------------------------------------
	# Rule 1: Editing software detected
	#-------------------------------------------
	if basic_exif.get("software"):
		indicators.append(f"Editing software detected: {basic_exif.get('software')}")
		risk_score += 2
		
	#-------------------------------------------------
	# Rule 2: EXIF present but capture data missing
	#-------------------------------------------------
	if basic_exif.get("has_exif") and extended_exif.get("has_extended_exif"):
		capture_fields = [
			extended_exif.get("exposure_time"), 
			extended_exif.get("f_number"), 
			extended_exif.get("iso_speed"), 
			extended_exif.get("focal_length")
			]
			
		if all(value is None for value in capture_fields):
			indicators.append("Camera capture parameters missing despite EXIF presence") 
			risk_score += 2
			
	#------------------------------------
	# Rule 3: No EXIF metadata at all
	#------------------------------------
	if not basic_exif.get("has_exif"):
		indicators.append("No EXIF metadata found (possible metadata stripping)")
		risk_score += 1
		
	#-------------------------------------------------
	# Rule 4: GPS data present but timestamp missing
	#-------------------------------------------------
	if basic_exif.get("gps_info") and not basic_exif.get("datetime_original"):
		indicators.append("GPS information present without original capture timestamp")
		risk_score += 1
		
	#-----------------------------------------------------------
	# Rule 5: Camera info present but capture settings missing
	#-----------------------------------------------------------
	if basic_exif.get("camera_make") and extended_exif.get("has_extended_exif"):
		if extended_exif.get("iso_speed") is None:
			indicators.append("Camera details present at capture settings incomplete")
			risk_score += 1
			
	#-------------------------------
	# Derive qualitative risk level
	#-------------------------------
	if indicators == []:
		indicators.append("None")
	if risk_score >= 4:
		risk_level = "High"
	elif risk_score >= 2:
		risk_level = "Medium"
	else:
		risk_level = "Low"
		
	return { 
		"metadata_risk_level": risk_level, 
		"risk_score": risk_score, 
		"forensic_indicators": indicators
		}

	
