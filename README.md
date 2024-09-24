# BBC News Classification

This project focuses on classifying BBC news articles into one of the predefined categories using machine learning techniques. The dataset used for this project consists of news articles from the BBC and includes categories such as **business**, **entertainment**, **politics**, **sport**, and **tech**.

## Project overview

The main goal of this project is to develop a model that can classify a given news article into its appropriate category based on its content. The project includes both unsupervised and supervised learning approaches to explore different techniques for text classification.

### Steps included:

1. **Data cleaning and preprocessing**:
   - Checked for missing values and removed duplicates.
   - Tokenized the text data and performed preprocessing (lowercasing, punctuation removal, etc.) for use in word embeddings.
   - Applied **Word2Vec** to transform the text data into word vectors.

2. **Unsupervised learning**:
   - Used **Non-negative Matrix Factorization (NMF)** to extract latent topics from the articles.
   - Classified the articles using a simple classifier based on these topics.

3. **Supervised learning**:
   - Built and evaluated models like **Random Forest** and **Logistic Regression** using TF-IDF and Word2Vec features.
   - Evaluated models based on metrics like accuracy, precision, recall, and F1-score.

4. **Model evaluation**:
   - Cross-validation was used to evaluate the models.
   - The **Random Forest** model achieved the highest accuracy, with strong performance across all categories.

## Results

- **Supervised learning** using Random Forest achieved a validation accuracy of **97.3%**.
- **Unsupervised learning** using NMF also provided insights into latent topics in the articles but achieved lower classification accuracy compared to supervised methods.

## Files in the repository

- `bbc_news_classification.ipynb`: Jupyter notebook containing the code for data preprocessing, model building, and evaluation.
- `bbc_news_test_predictions.csv`: Output predictions for the test set.
- `word2vec_bbc.model`: Word2Vec model trained on the BBC news articles.
- `cleaned_data.csv`: Cleaned and preprocessed data used for model training.
- `cleaned_data_word2vec.csv`: Preprocessed data transformed into Word2Vec features.

## Usage

To run this project locally, clone the repository and open the Jupyter notebook:

```bash
git clone https://github.com/yourusername/bbc_news_classification.git
cd bbc_news_classification
jupyter notebook bbc_news_classification.ipynb
