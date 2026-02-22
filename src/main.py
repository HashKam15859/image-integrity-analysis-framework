import joblib
from intake.image_loader import load_image
from metadata.exif_analyzer import extract_exif_metadata
from metadata.exif_extended import extract_extended_exif
from metadata.metadata_analyzer import analyze_metadata_consistency
from metadata.file_metadata import extract_file_encoding_metadata
from forensics.forensic_scoring import compute_forensic_score
from content.content_forensics import analyze_image_content
from steganography.steganalysis import analyze_steganography
from ai.feature_builder import build_feature_vector

# Load trained AI model (once at startup)
MODEL_PATH = "models/forensic_rf_model.pkl"

try: 
	ai_model = joblib.load(MODEL_PATH)
	AI_AVAILABLE = True
except Exception: 
	ai_mode = None
	AI_AVAILABLE = False
# Entry point of the Digital Image Forensics Tool

if __name__ == "__main__":
	# Ask the user for the image file path
	image_path = input("Enter the path to the image file: ").strip()
	
	try: 
		# Perform the image intake and forensic validation
		forensic_info = load_image(image_path)
		
		# Display the forensic intake report
		print("\n--- Image Intake & Integrity Report ---")
		for key, value in forensic_info.items():
			print(f"{key}: {value}")
			
		# Perform EXIF metadata extraction
		exif_info = extract_exif_metadata(image_path)
		
		print("\n---Basic EXIF Metadata ---")
		for key, value in exif_info.items():
			print(f"{key}: {value}")
			
		# Extended EXIF capture metadata extraction
		extended_exif = extract_extended_exif(image_path)
		
		print("\n--- Extended EXIF Capture Details----")
		for key, value in extended_exif.items():
			print(f"{key}: {value}")	
			
		# Metadata consistency analysis
		metadata_analysis = analyze_metadata_consistency(exif_info, extended_exif)
		
		print("\n--- Metadata Consistency Analysis ---")
		print(f"Metadata Risk Level: {metadata_analysis['metadata_risk_level']}")
		print(f"Risk Score: {metadata_analysis['risk_score']}")
		
		print("Forensic Indicators: ")
		for indicator in metadata_analysis["forensic_indicators"]:
			print(f"- {indicator}")
			
		# File Encoding & compression metadata
		file_encoding = extract_file_encoding_metadata(image_path)
		
		print("\n--- File Encoding & Compression Metadata ---")
		for key, value in file_encoding.items():
			print(f"{key}: {value}")
		
		# Image content forensics
		content_analysis = analyze_image_content(image_path)
		
		print("\n--- Image Content Forensics ---")
		print(f"Content Score: {content_analysis['score']}")
		for obs in content_analysis["observations"]:
			print(f"- {obs}")
			
		# Steganography detection
		steg_analysis = analyze_steganography(image_path)
		
		print("\n--- Steganography Detection ---")
		print(f"Steganalysis Score: {steg_analysis['score']}")
		for obs in steg_analysis["observations"]:
			print(f"- {obs}")
			
		# Unified forensic scoring
		forensic_result = compute_forensic_score(
			metadata_analysis = metadata_analysis, 
			file_encoding_metadata = file_encoding, 
			content_forensics = content_analysis,
			steganalysis = steg_analysis
			)
		
		# Build AI feature vector (AI-ready input)
		feature_vector = build_feature_vector(
			exif_info=exif_info, 
			metadata_analysis=metadata_analysis, 
			file_encoding=file_encoding, 
			content_analysis=content_analysis,
			steg_analysis=steg_analysis,
			rule_based_score=forensic_result["unified_score"]
			)
			
		#-----------------------------------
		# AI Inference (if model available)
		#-----------------------------------
		if AI_AVAILABLE: 
			# Reshape for sklearn (expects 2D array)
			ai_probability = ai_model.predict_proba(feature_vector.reshape(1, -1))[0][1] # Probability of "manipulated" class
			ai_decision = "Manipulated" if ai_probability >= 0.5 else "Likely Authentic"
		else: 
			ai_probability = None
			ai_decision = "AI model not available"
		
		print("\n--- AI Feature Vector ----")
		print(feature_vector)
		print("Feature Vector Length: ", len(feature_vector))
		
		print("\n==== Unified Forensic Assessment ====")
		print(f"Unified Score: {forensic_result['unified_score']}")
		print(f"Risk Level: {forensic_result['risk_level']}")
		print("\nForensic Summary:")
		print(forensic_result["forensic_summary"])
		print("\n---- AI-Assisted Assessment ---")
		if AI_AVAILABLE: 
			print(f"AI Probability of Manipulation: {ai_probability:.2f}")
			print(f"AI Decision: {ai_decision}")
		else: 
			print("AI model not loaded. Skipping AI-based assessment.")
		
			
	except Exception as error:
		# Catch and display any errors in a user-friendly manner
		print(f"\nError during image analysis: {error}")
