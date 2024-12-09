import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional
from tensorflow.keras.utils import to_categorical

def load_trained_model(timesteps, features):
    # Define the model structure
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=False), input_shape=(timesteps, features)),
        Dense(64, activation='relu'),
        Dense(2, activation='softmax')
    ])
    # Compile the model (assuming it has been pre-trained and weights are loaded)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Load pre-trained weights
    # Replace 'model_weights.h5' with the path to your saved model weights file
    model.load_weights('model_weights.h5')
    
    return model

def preprocess_image(image_path, img_size=(256, 256), patch_size=(256, 256)):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, img_size)
    
    patches = []
    for i in range(0, img.shape[0], patch_size[0]):
        for j in range(0, img.shape[1], patch_size[1]):
            patch = img[i:i+patch_size[0], j:j+patch_size[1]].flatten()
            patches.append(patch)
    return np.array([patches])  # Return as batch of 1 for model compatibility

def verify_signature(image_path):
    # Load and preprocess the image
    processed_image = preprocess_image(image_path)
    
    # Load the model with the correct input dimensions
    timesteps, features = processed_image.shape[1], processed_image.shape[2]
    model = load_trained_model(timesteps, features)
    
    # Predict the class
    prediction = model.predict(processed_image)
    predicted_class = np.argmax(prediction, axis=1)[0]
    
    # Return "Yes" for genuine and "No" for forged
    return "Yes" if predicted_class == 0 else "No"

# Usage
image_path = "path/to/your/test_signature_image.jpg"
result = verify_signature(image_path)
print(result)
