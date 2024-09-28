## Disaster Tweets Classification
This project involves classifying tweets into two categories: disaster-related and non-disaster-related. The goal is to accurately identify whether a given tweet is referring to a real disaster or not.

### Project Overview
The dataset consists of tweets labeled as either disaster (1) or non-disaster (0). The project includes data preprocessing, feature engineering, model training, and evaluation using various machine learning algorithms, with a focus on performance optimisation.

### Workflow

#### Data Preprocessing:

Convert text to lowercase.
Replace abbreviations and handle emojis.
Remove stopwords, HTML tags, URLs, and special characters.
Tokenization and vectorization (TF-IDF).

#### Model Training:

Logistic Regression (best model, 79.6% accuracy).
Random Forest (79% accuracy).
LSTM with Word2Vec embeddings (best accuracy: 68.65% after hyperparameter tuning).

#### Hyperparameter Tuning:

Adjusted LSTM units, dropout rate, batch size, and number of epochs.
Evaluated models based on validation accuracy to optimize performance.

#### Final Model:

Logistic Regression selected as the final model for submission due to its superior accuracy and simplicity.

### Conclusion
Logistic Regression achieved the highest accuracy (79.6%), making it the best model for this task. Further improvements could be made by experimenting with advanced deep learning architectures like Transformers or incorporating additional features.
