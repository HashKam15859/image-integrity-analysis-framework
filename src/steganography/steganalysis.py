import cv2
import numpy as np
from math import log2

def safe_mean(array):
	""" Computes mean safely.
	Returns None if array is empty or invalid. """ 
	if array is None or array.size == 0:
		return None
	if np.isnan(array).any():
		return None
	return np.mean(array)

def shannon_entropy(data):
	""" Computes Shannon entropy of a grayscale image array. 
	Higher entropy may indicate hidden data or heavy processing. """
	
	histogram, _ = np.histogram(data, bins=256, range=(0, 256))
	
	total = np.sum(histogram)
	if total == 0:
		return None
	histogram = histogram / total
	
	entropy = 0
	for p in histogram:
		if p > 0: 
			entropy -= p * log2(p)
			
	return entropy
	
def analyze_steganography(image_path):
	""" Performs statistical steganalysis to detect indicators of possible hidden data within an image. """
	observations = []
	score = 0
	
	# Load image in grayscale
	image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
	
	if image is None:
		return {
			"score": 0, 
			"observations": ["Unable to load image for steganalysis."]
			}
	
	#--------------------------------
	# 1. LSB Plane Analysis
	#--------------------------------
	# Extract least significant bit plane
	lsb_plane = image & 1
	lsb_variance = np.var(lsb_plane) if lsb_plane.size > 0 else None
	
	# High variance may indicate artificial randomness
	if lsb_variance is not None and lsb_variance > 0.25: 
		observations.append("Irregular LSB patterns detected (possible hidden data).")
		score += 2
	#----------------------
	# 2. Entropy Analysis
	#----------------------
	entropy = shannon_entropy(image)
	
	# Natural images typically have entropy below extreme randomness 
	if entropy is not None and entropy > 7.5:
		observations.append("High entropy detected (possible steganographic modification).")
		score += 1
	
	#-------------------------------
	# 3. Histogram Smoothness Check
	#-------------------------------
	histogram = cv2.calcHist([image], [0], None, [256], [0, 256])
	if histogram is not None and histogram.size > 1:
		diff = np.diff(histogram.flatten())
		histogram_diff = safe_mean(np.abs(diff))
		
	
		if histogram_diff is not None and histogram_diff < 0.5: 
			observations.append("Abnormally smooth histogram detected.")
			score += 1
	else: 
		histogram_diff = None
		
	#----------------------------
	# 4. Noise Residual Analysis
	#----------------------------
	noise = image.astype(np.float32) - cv2.GaussianBlur(image, (5, 5), 0)
	noise_var = np.var(noise) if noise.size > 0 else None
	
	if noise_var is not None and noise_var > 30: 
		observations.append("Noise residuals suggest possible data embedding.")
		score += 1
		
	#---------------------------
	# Final steganalysis result
	#---------------------------
	if not observations:
		observations.append("No strong statistical indicators of steganography detected.")
		
	return { 
		"score": score, 
		"observations": observations, 
		"entropy": round(entropy, 3),
		"lsb_variance": round(lsb_variance, 4),
		"noise_variance": round(noise_var, 2)
		}

