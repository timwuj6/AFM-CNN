# AFM_CNN
Characterizing 2D Materials with Semi-Supervised Learning and Convolutional Neural Networks
AFM Image Analysis by CNN
This project aims to develop a deep learning model based on convolutional neural networks (CNN) to analyze WSe2 thin film coverage from Atomic Force Microscopy (AFM) images.


# Dataset
The dataset used in this project consists of 2122 AFM images acquired and augmented from Joan Redwing's research group from Pennsylvania State University Materials Research Institute. Each image is a 3D array of height values (in nm) representing the surface topography. The dataset is divided into a training set and a validation set, with respective proportions of 80% and 20%.

# Model Architecture
The CNN model used in this project consists of several convolutional and pooling layers, followed by a few fully connected layers. The input to the model is a 3D array of AFM image pixels, and the output is a set of predicted labels corresponding to the task at hand (e.g., roughness, particle count).



# Results
The trained model achieves a root mean square error of 3.8% on the test set from fine tuned MicrNet encoder. The model can be further improved by increasing the dataset size, fine-tuning the hyperparameters, or using more advanced CNN architectures.

# References
Zhang, X.,et al. (2018). Diffusion-controlled epitaxy of large area coalesced \ce{WSe2} monolayers on Sapphire. \emph{Nano Letters}, 18(2), 1049–1056.https://doi.org/10.1021/acs.nanolett.7b04521
