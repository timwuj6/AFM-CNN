# AFM_CNN
Characterizing 2D Materials with Semi-Supervised Learning and Convolutional Neural Networks
AFM Image Analysis by CNN
This project aims to develop a deep learning model based on convolutional neural networks (CNN) to analyze Atomic Force Microscopy (AFM) images. The model can be used for tasks such as surface roughness analysis, particle counting, and feature recognition.

# Requirements
Python 3.x
TensorFlow 2.x or higher
NumPy
Matplotlib
Scikit-image

# Dataset
The dataset used in this project consists of AFM images acquired from various samples. Each image is a 2D array of height values (in nm) representing the surface topography. The dataset is divided into a training set, a validation set, and a test set, with respective proportions of 70%, 15%, and 15%.

# Model Architecture
The CNN model used in this project consists of several convolutional and pooling layers, followed by a few fully connected layers. The input to the model is a 2D array of AFM image pixels, and the output is a set of predicted labels corresponding to the task at hand (e.g., roughness, particle count).

# Training
To train the model, run the train.py script. The script loads the dataset, initializes the model, and trains the model on the training set using stochastic gradient descent. The script saves the trained model weights in a checkpoint file.

# Evaluation
To evaluate the trained model, run the evaluate.py script. The script loads the test set, loads the trained model weights from the checkpoint file, and evaluates the model on the test set. The evaluation metrics include accuracy, precision, recall, and F1-score.


# Results
The trained model achieves a mean accuracy of X% on the test set for the task of Y. The model can be further improved by increasing the dataset size, fine-tuning the hyperparameters, or using more advanced CNN architectures.

# References
[List any relevant references or sources used in the project]
