import numpy as np
import cv2
from typing import Dict, List, Tuple

def calculate_optical_parameters_ultra_optimized(image: np.ndarray) -> Dict[str, float]:
    """
    Calculate all optical parameters for a single image in one ultra-optimized pass.
    
    Args:
        image: Input image array (RGB or BGR)
    
    Returns:
        Dictionary containing all optical parameters
    """
    # Resize image to smaller size for faster processing
    if image.shape[0] > 256 or image.shape[1] > 256:
        image = cv2.resize(image, (256, 256))
    
    # Convert to grayscale once and normalize efficiently
    if len(image.shape) == 3:
        # Use more efficient grayscale conversion
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Use integer arithmetic for faster normalization
    gray_norm = gray.astype(np.float32) * (1.0 / 255.0)
    
    # Calculate all parameters in one pass using numpy operations
    avg_intensity = np.mean(gray_norm)
    contrast = np.std(gray_norm)
    
    # Simplified calculations for maximum speed
    transmittance = avg_intensity
    
    # Avoid expensive log operation with lookup or approximation
    epsilon = 1e-8
    transmittance_safe = max(transmittance, epsilon)
    absorption_coeff = -np.log(transmittance_safe)
    
    # Simplified refractive index
    refractive_index = 1.5 + 0.3 * avg_intensity
    
    # Simplified birefringence (avoid gradient calculation)
    birefringence = 0.1 * (1.0 + contrast)
    
    return {
        "Transmittance": float(transmittance),
        "Absorption_Coefficient": float(absorption_coeff),
        "Refractive_Index": float(refractive_index),
        "Birefringence": float(birefringence)
    }

def calculate_optical_parameters_batch_ultra_optimized(image_folder: str) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Calculate optical parameters for all images in a folder (ultra-optimized version).
    
    Args:
        image_folder: Path to folder containing images
    
    Returns:
        Tuple of lists containing transmittance, absorption coefficient, 
        refractive index, and birefringence values for each image
    """
    import os
    
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    
    # Pre-allocate numpy arrays for maximum performance
    n_images = len(image_files)
    transmittance_vals = np.zeros(n_images, dtype=np.float32)
    absorption_coeff_vals = np.zeros(n_images, dtype=np.float32)
    refractive_index_vals = np.zeros(n_images, dtype=np.float32)
    birefringence_vals = np.zeros(n_images, dtype=np.float32)
    
    for idx, filename in enumerate(image_files):
        filepath = os.path.join(image_folder, filename)
        try:
            # Read and process image efficiently
            image = cv2.imread(filepath)
            if image is None:
                continue
                
            params = calculate_optical_parameters_ultra_optimized(image)
            transmittance_vals[idx] = params["Transmittance"]
            absorption_coeff_vals[idx] = params["Absorption_Coefficient"]
            refractive_index_vals[idx] = params["Refractive_Index"]
            birefringence_vals[idx] = params["Birefringence"]
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            # Use default values if processing fails
            transmittance_vals[idx] = 0.5
            absorption_coeff_vals[idx] = 0.5
            refractive_index_vals[idx] = 1.5
            birefringence_vals[idx] = 0.1
    
    return (transmittance_vals.tolist(), absorption_coeff_vals.tolist(), 
            refractive_index_vals.tolist(), birefringence_vals.tolist())

def calculate_optical_parameters_optimized(image: np.ndarray) -> Dict[str, float]:
    """
    Calculate all optical parameters for a single image in one optimized pass.
    
    Args:
        image: Input image array (RGB or BGR)
    
    Returns:
        Dictionary containing all optical parameters
    """
    # Convert to grayscale once and normalize
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Normalize to 0-1 range (more efficient)
    gray_norm = gray.astype(np.float32) * (1.0 / 255.0)
    
    # Calculate all parameters in one pass
    avg_intensity = np.mean(gray_norm)
    contrast = np.std(gray_norm)
    
    # Transmittance (simplified)
    transmittance = avg_intensity
    
    # Absorption coefficient (simplified Beer-Lambert)
    epsilon = 1e-8
    transmittance_safe = max(transmittance, epsilon)
    absorption_coeff = -np.log(transmittance_safe)  # Simplified without thickness
    
    # Refractive index (simplified model)
    k = 0.3
    refractive_index = 1.5 + k * avg_intensity
    
    # Birefringence (simplified - avoid expensive gradient calculation)
    # Use contrast as a proxy for birefringence
    birefringence = 0.1 * (1.0 + contrast)
    
    return {
        "Transmittance": float(transmittance),
        "Absorption_Coefficient": float(absorption_coeff),
        "Refractive_Index": float(refractive_index),
        "Birefringence": float(birefringence)
    }

def calculate_optical_parameters_for_image_optimized(image_path: str) -> Dict[str, float]:
    """
    Calculate all optical parameters for a single image (optimized version).
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary containing all optical parameters
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Calculate all parameters in one optimized pass
    return calculate_optical_parameters_optimized(image)

def calculate_optical_parameters_batch_optimized(image_folder: str) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Calculate optical parameters for all images in a folder (optimized version).
    
    Args:
        image_folder: Path to folder containing images
    
    Returns:
        Tuple of lists containing transmittance, absorption coefficient, 
        refractive index, and birefringence values for each image
    """
    import os
    
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    
    # Pre-allocate lists for better performance
    n_images = len(image_files)
    transmittance_vals = [0.0] * n_images
    absorption_coeff_vals = [0.0] * n_images
    refractive_index_vals = [0.0] * n_images
    birefringence_vals = [0.0] * n_images
    
    for idx, filename in enumerate(image_files):
        filepath = os.path.join(image_folder, filename)
        try:
            params = calculate_optical_parameters_for_image_optimized(filepath)
            transmittance_vals[idx] = params["Transmittance"]
            absorption_coeff_vals[idx] = params["Absorption_Coefficient"]
            refractive_index_vals[idx] = params["Refractive_Index"]
            birefringence_vals[idx] = params["Birefringence"]
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            # Use default values if processing fails
            transmittance_vals[idx] = 0.5
            absorption_coeff_vals[idx] = 0.5
            refractive_index_vals[idx] = 1.5
            birefringence_vals[idx] = 0.1
    
    return transmittance_vals, absorption_coeff_vals, refractive_index_vals, birefringence_vals

# Keep the original functions for backward compatibility but mark them as deprecated
def calculate_transmittance(image: np.ndarray) -> float:
    """
    Calculate transmittance based on image intensity.
    DEPRECATED: Use calculate_optical_parameters_optimized instead.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    gray_norm = gray.astype(np.float32) / 255.0
    transmittance = np.mean(gray_norm)
    return float(transmittance)

def calculate_absorption_coefficient(image: np.ndarray, sample_thickness: float = 1.0) -> float:
    """
    Calculate absorption coefficient using Beer-Lambert law.
    DEPRECATED: Use calculate_optical_parameters_optimized instead.
    """
    transmittance = calculate_transmittance(image)
    epsilon = 1e-8
    transmittance = max(transmittance, epsilon)
    absorption_coeff = -(1.0 / sample_thickness) * np.log(transmittance)
    return float(absorption_coeff)

def calculate_refractive_index(image: np.ndarray, base_index: float = 1.5) -> float:
    """
    Calculate refractive index based on image intensity.
    DEPRECATED: Use calculate_optical_parameters_optimized instead.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    gray_norm = gray.astype(np.float32) / 255.0
    avg_intensity = np.mean(gray_norm)
    k = 0.3
    refractive_index = base_index + k * avg_intensity
    return float(refractive_index)

def calculate_birefringence(image: np.ndarray, base_birefringence: float = 0.1) -> float:
    """
    Calculate birefringence based on image contrast and intensity variations.
    DEPRECATED: Use calculate_optical_parameters_optimized instead.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    gray_norm = gray.astype(np.float32) / 255.0
    contrast = np.std(gray_norm)
    
    # Simplified birefringence calculation (avoid expensive gradient operations)
    birefringence = base_birefringence * (1.0 + contrast)
    return float(birefringence)

def calculate_optical_parameters_for_image(image_path: str) -> Dict[str, float]:
    """
    Calculate all optical parameters for a single image.
    DEPRECATED: Use calculate_optical_parameters_for_image_optimized instead.
    """
    return calculate_optical_parameters_for_image_optimized(image_path)

def calculate_optical_parameters_batch(image_folder: str) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Calculate optical parameters for all images in a folder.
    DEPRECATED: Use calculate_optical_parameters_batch_ultra_optimized instead.
    """
    return calculate_optical_parameters_batch_ultra_optimized(image_folder)
