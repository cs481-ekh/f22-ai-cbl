![pylint workflow](https://github.com/cs481-ekh/f22-ai-cbl/actions/workflows/pylint.yml/badge.svg)

# Knee Stress Prediction

### Members:
- Nina Nikitina
- Harry Hsu
- Stephanie Ball

### Abstract

Our project was purely a research project in which the goal is to create and test a machine learning algorithm that can predict knee peak stress/strain with a specified accuracy based on the geometry of the knee and loading conditions. More specifically, we wanted to predict peak stress/strain on the lateral and medial cartilage on the tibia. 

We followed the standard Machine Learning approach starting with data cleaning, then feature engineering, followed by training and testing the model. The process of training and testing the model was repeated each time we created a new feature or performed data cleaning. For the model, our goal was to use three different machine learning algorithms and determine which had the best results. 

During our research project, we were given three different sets of data to train and test our models. The first dataset had geometry of one knee with pressure/strain for 100 time points. The time points come from the motion of a knee moving from a standing position to a squatting position. The second set of data consisted of 28 knees with 240 time points and the third dataset had 169 knees with 240 time points. 

Most of our time was spent on data cleaning and extracting new features. We were able to extract new features by determining whether or not the cartilage is healthy or unhealthy. We also measured curvature of the cartilage.


### Project Description
Across the project, we have built three machine-learning models designed to do different tasks. We have a multiple-feature linear regressor model which processes through the entire dataset and works toward generating a model that can predict peak stress in complex features. On top of that, we have built non-linear decision trees regressor model with the help of Scikit Learn. The purpose of creating such a model is to compare and analyze the data from the different mathematical models and to cross-validation to ensure we can select the optimal model for this research. 
Besides supervised machine learning, we have implemented K-Means Clustering,  an unsupervised machine learning built as the supporting machine to analyze the data and justify the outcome of random forests and linear regressor. We implemented the elbow method to use a statical strategy to select the correct number of clusters. As optimal outcomes, 3 clusters represent low, medium, and peak stress. So this method act as proof of data engineering as well. After implementation, we obtained 3 clusters as recommendations from the method, proving that data engineering is effective. 


