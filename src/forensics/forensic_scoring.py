def compute_forensic_score(metadata_analysis, file_encoding_metadata, content_forensics=None, steganalysis=None):
	""" Computes a unified forensic score by correlating multiple forensic signals. 
	The score reflects the likelihood of image manipulation.
	
	Inputs: 
	- metadata_analysis: output from metadata consistency analysis
	- file_encoding_metadata: output from encoding/compression analysis
	- content_forensics: (optional) future OpenCV-based analysis
	- steganalysis: (optional) future steganography detection
	
	Output: 
	- Unified score, risk level, and explanatory narrative """
	
	total_score = 0
	explanations = []
	
	#---------------------------------
	# 1. Metadata consustency Signals
	#---------------------------------
	meta_risk = metadata_analysis.get("risk_score", 0)
	
	# Weight metadata signals moderately (important but not decisive alone)
	total_score += meta_risk * 2
	
	if meta_risk > 9: 
		explanations.append(f"Metadata analysis indicates {metadata_analysis.get('metadata_risk_level')} risk.")
		for indicator in metadata_analysis.get("Forensic_indicators", []):
			explanations.append(f"Metadata indicator: {indicator}")
	
	#----------------------------------------
	# 2. File Encoding & Compression Signals
	#----------------------------------------
	#JPEG recompression indicators
	if file_encoding_metadata.get("image_format") == "JPEG":
		subsampling = file_encoding_metadata.get("chroma_subsampling")
		
		# Lossy subsampling patterns suggest recompression
		if subsampling in ["4:2:0", "4:2:2"]:
			total_score += 2
			explanations.append(f"Lossy JPEG chroma subsampling detected ([subsampling]).")
	
	# Compression metadata presence
	if file_encoding_metadata.get("compression"):
		total_score += 1
		explanations.append(f"Image uses compression method: {file_encoding_metadata.get('compression')}.")
		
	#------------------------------------
	# 3. Content Forensics (Future Hook)
	#------------------------------------
	if content_forensics:
		content_score = content_forensics.get("score", 0)
		total_score += content_score
		explanations.append("Content-based forensic analysis contributed to overall score.")
	
	#-------------------------------
	# 4. Steganalysis (Future Hook)
	#-------------------------------
	
	if steganalysis: 
		steg_score = steganalysis.get("score", 0)
		total_score += steg_score
		explanations.append("Steganography indicators influenced forensic assessment.")
	
	#-----------------------------------
	# 5. Final Risk Level Determination
	#-----------------------------------
	if total_score >= 8:
		risk_level = "High"
	elif total_score >= 4:
		risk_level = "Medium"
	else: 
		risk_level = "Low"
		
	#-------------------------------
	# 6. Forensic Narrative Summary
	#-------------------------------
	narrative = generate_forensic_narrative(risk_level, explanations)
	
	return {
		"unified_score": total_score,
		"risk_level": risk_level, 
		"explanations": explanations, 
		"forensic_summary": narrative
		}

def generate_forensic_narrative (risk_level, explanations):
	""" Generates a human-readable forensic summary based on correlated forensic indicators. """
	if risk_level == "High": 
		opening = ("\nThe forensic analysis indicates a high likelihood of image manipulation.")
	elif risk_level == "Medium":
		opening = ("\nThe forensic analysis indicates a moderate likelihood of image manipulation")
	else: 
		opening = ("\nThe forensic analysis indicates a low likelihood of image manipulation.")
	
	if explanations: 
		details = "\nKey contributing factors include: "
		details += " ; ".join(explanations)
	else: 
		details = ("\nNo significant forensic inconsistencies were identified across analyzed indicators.")
		
	return opening + details

