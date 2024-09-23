import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import io

# Load the YAMNet model
model = hub.load('https://www.kaggle.com/models/google/yamnet/TensorFlow2/yamnet/1')

# Create a sample input (3 seconds of silence as an example)
waveform = np.zeros(3 * 16000, dtype=np.float32)

# Run the model to get its outputs
scores, embeddings, log_mel_spectrogram = model(waveform)

# Verify the shapes
print(f"Scores shape: {scores.shape}")
print(f"Embeddings shape: {embeddings.shape}")
print(f"Log mel spectrogram shape: {log_mel_spectrogram.shape}")

# Function to get class names from the CSV
def class_names_from_csv(class_map_csv_text):
    class_map_csv = io.StringIO(class_map_csv_text)
    class_names = [display_name for (class_index, mid, display_name) in csv.reader(class_map_csv)]
    class_names = class_names[1:]  # Skip CSV header
    return class_names

# Get the class names
class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(tf.io.read_file(class_map_path).numpy().decode('utf-8'))

# Print the predicted class for the sample input
print(f"Predicted class: {class_names[scores.numpy().mean(axis=0).argmax()]}")

# Save the model in SavedModel format
tf.saved_model.save(model, '/home/khadas/alog/models/yamnet/yamnet_savedmodel')
print("Model saved in SavedModel format.")

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model('/home/khadas/alog/models/yamnet/yamnet_savedmodel')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float32]  # Changed from float16 to float32
tflite_model = converter.convert()

# Save the TFLite model
with open('/home/khadas/alog/models/yamnet/yamnet_optimized.tflite', 'wb') as f:
    f.write(tflite_model)

print("Model converted and saved as yamnet_optimized.tflite")