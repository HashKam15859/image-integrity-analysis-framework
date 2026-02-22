import cv2
import numpy as np

def safe_variance(array):
	""" Computes variance safely.
	Returns None if the array is empty or invalid. """
	if array is None or array.size == 0:
		return None
	if np.isnan(array).any():
		return None
	return np.var(array)


def analyze_image_content(image_path):
	""" Performs content-based image forensic analysis using pixel-level and statistical indicators. 
	Returns a score and a list of forensic observations. """
	
	observations = []
	score = 0
	
	#---------------------------------
	# Step 1: Load image using OpenCV
	#---------------------------------
	image = cv2.imread(image_path)
	
	if image is None: 
		return {
			"score": 0, 
			"observations": ["Unable to load image for content analysis."]
			}
	
	# Convert to grayscale for statistical analysis
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	
	if gray.dtype != "uint8":
		gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")
	
	#-----------------------------------
	# Step 2: Noise Analysis (Variance)
	#-----------------------------------
	# Natural images have relatively consistent noise patterns. 
	noise = gray.astype(np.float32) - cv2.GaussianBlur(gray, (5, 5), 0)
	noise_variance = np.var(noise)
	
	if noise_variance is not None and noise_variance > 20: 
		observations.append("High noise variance detected (possible manipulation or recompression).")
		score += 2
		
	#-------------------------------
	# Step 3: Edge Density Analysis
	#-------------------------------
	# Manipulated regions often introduce unnatural edge patterns. 
	edges = cv2.Canny(gray, 100, 200)
	
	if edges is not None and edges.size > 0:
		edge_density = np.sum(edges > 0) / edges.size
		if edge_density > 0.1: 
		
			observations.append("Unusually high edge density detected.")
			score += 1
		
	#----------------------------------------
	# Step 4: Texture Consistency (Laplacian)
	#----------------------------------------
	laplacian = cv2.Laplacian(gray, cv2.CV_64F)
	laplacian_var = safe_variance(laplacian)
	
	if laplacian_var is not None and laplacian_var > 500:
		observations.append("Texture irregularities detected in image content.")
		score += 1
	 	
 	#---------------------------------------
 	# Step 5: Final content forensic result
 	#---------------------------------------
	if not observations:
		observations.append("No significant content-level forensic anomalies detected.")
 		
	return {
		"score": score, 
		"observations": observations, 
		"noise_variance": round(noise_variance, 2),
		"edge_density": round(edge_density, 4), 
		"texture_variance": round(laplacian_var, 2)
		}
