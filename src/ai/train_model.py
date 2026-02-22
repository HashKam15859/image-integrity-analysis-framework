""" AI Training Pipeline for Digital Image Forensics Tool

This script: 
- Extracts forensic features from images
- Builds feature vectors
- Trains a Random Forest classifier
- Evaluates performance
- Saves the trained model """

print(">>> train_model.py started")

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix, roc_auc_score

# Import forensic modules
from src.intake.image_loader import load_image
from src.metadata.exif_analyzer import extract_exif_metadata
from src.metadata.exif_extended import extract_extended_exif
from src.metadata.metadata_analyzer import analyze_metadata_consistency
from src.metadata.file_metadata import extract_file_encoding_metadata
from src.content.content_forensics import analyze_image_content
from src.steganography.steganalysis import analyze_steganography
from src.forensics.forensic_scoring import compute_forensic_score
from src.ai.feature_builder import build_feature_vector

DATASET_PATH = "dataset"

def extract_features_from_image(image_path): 
	""" Runs the full forensic pipeline on an image and returns its AI feature vector. """
	# Forensic analysis pipeline
	exif_data = extract_exif_metadata(image_path)
	extended_exif = extract_extended_exif(image_path)
	
	metadata_analysis = analyze_metadata_consistency(exif_data, extended_exif)
	file_encoding = extract_file_encoding_metadata(image_path)
	content_analysis = analyze_image_content(image_path)
	steg_analysis = analyze_steganography(image_path)
	
	rule_based_result = compute_forensic_score(
		metadata_analysis = metadata_analysis, 
		file_encoding_metadata = file_encoding, 
		content_forensics = content_analysis, 
		steganalysis = steg_analysis
		)
		
	# Build AI feature vector
	feature_vector = build_feature_vector(
		exif_info=exif_data, 
		metadata_analysis=metadata_analysis, 
		file_encoding=file_encoding,
		content_analysis=content_analysis, 
		steg_analysis=steg_analysis, 
		rule_based_score=rule_based_result["unified_score"]
		)
	return feature_vector
	
def load_dataset(): 
	""" Loads images from dataset folders and buiilds x, y. """
	
	x = []
	y =  []
	
	for label_name, label_value in [("original", 0), ("manipulated", 1)]: 
		folder = os.path.join(DATASET_PATH, label_name)
		
		for file_name in os.listdir(folder):
			image_path = os.path.join(folder, file_name)
			
			try: 
				features = extract_features_from_image(image_path)
				x.append(features)
				y.append(label_value)
				
			except Exception as e: 
				print(f"Skipping {image_path}: {e}")
				
	return np.array(x), np.array(y)
	
def train_model():
	print(">>> train_model() has entered")
	""" Trains and evaluates the Random Forest model. """
	
	print("[*] Loading dataset......")
	x, y = load_dataset()
	
	print(f"[*] Dataset loaded: {len(x)} samples")
	
	# Train test split
	x_train, x_test, y_train, y_test = train_test_split(
		x, y, 
		test_size=0.3, 
		random_state=42, 
		stratify=y
	)
	
	#Initialize Random Forest
	model = RandomForestClassifier(n_estimators=100, random_state=42)
	cv_scores = cross_val_score(model, x, y, cv=5)
	
	print("\n==== Cross Validation ====")
	print(f"CV Accuracy Mean: {cv_scores.mean():.3f}")
	print(f"CV Std Dev: {cv_scores.std():.3f}")
	
	print("[*] Training model....")
	model.fit(x_train, y_train)
	
	# Prediction 
	y_pred = model.predict(x_test)
	
	probs = model.predict_proba(x_test)[:,1]
	auc = roc_auc_score(y_test, probs)
	print(f"AUC: {auc:.3f}")
	
	# Evaluation
	accuracy = accuracy_score(y_test, y_pred)
	precision = precision_score(y_test, y_pred, zero_division=0)
	recall = recall_score(y_test, y_pred, zero_division=0)
	
	cm = confusion_matrix(y_test, y_pred)
	print("\nConfusion Matrix: ")
	print(cm)
	
	print("\n=== Model Evaluation ===")
	print(f"Accuracy: {accuracy:.3f}")
	print(f"Precision: {precision:.3f}")
	print(f"Recall: {recall:.3f}")
	
	# Feature Importance Analysis
	feature_names = [
		"metadata_risk_score", 
		"has_exif", 
		"editing_software_detected", 
		"is_jpeg", 
		"jpeg_lossy_subsampling", 
		"compression_present", 
		"noise_variance", 
		"edge_density", 
		"texture_variance",
		"entropy", 
		"lsb_variance",
		"steganalysis_score", 
		"rule_based_score"
	]
	
	importances = model.feature_importances_
	
	print("\n==== Feature Importance ====")
	for name, score in zip(feature_names, importances): 
		print(f"{name}: {score:.3f}")
	
	# Saved trained model
	os.makedirs("models", exist_ok=True)
	joblib.dump(model, "models/forensic_rf_model.pkl")
	
	print("\n[*] Model saved as models/forensic_rf_model.pkl")
	
if __name__ == "__main__":
	train_model()
