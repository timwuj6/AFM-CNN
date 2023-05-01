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
Ronneberger, O., Fischer, P., Brox, T. (2015). U-Net: Convolutional Networks for Biomedical Image Segmentation. In: Navab, N., Hornegger, J., Wells, W., Frangi, A. (eds) Medical Image Computing and Computer-Assisted Intervention – MICCAI 2015. MICCAI 2015. Lecture Notes in Computer Science(), vol 9351. Springer, Cham.
https://doi.org/10.1007/978-3-319-24574-4_28

Zhang, X.,et al. (2018). Diffusion-controlled epitaxy of large area coalesced WSe2 monolayers on Sapphire. Nano Letters, 18(2), 1049–1056. https://doi.org/10.1021/acs.nanolett.7b04521 

Tan, M., & Le, Q. (2019, May). Efficientnet: Rethinking model scaling for convolutional neural networks. In International conference on machine learning (pp. 6105-6114). PMLR. https://arxiv.org/abs/1905.11946

Su, Chao & Wang, Wenjun. (2020). Concrete Cracks Detection Using Convolutional NeuralNetwork Based on Transfer Learning. Mathematical Problems in Engineering. 2020. 1-10. doi 10.1155/2020/7240129. 

J. Deng,et al, "ImageNet: A large-scale hierarchical image database," 2009 IEEE Conference on Computer Vision and Pattern Recognition, Miami, FL, USA, 2009, pp. 248-255, doi: 10.1109/CVPR.2009.5206848.

Stuckner, J., et al. Microstructure segmentation with deep learning encoders pre-trained on a large microscopy dataset. npj Comput Mater8, 200 (2022). https://doi.org/10.1038/s41524-022-00878-5

He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR). https://doi.org/10.1109/cvpr.2016.90 
