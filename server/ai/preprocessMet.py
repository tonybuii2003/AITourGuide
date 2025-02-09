import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

data = pd.read_csv('/Users/flying-dragon03/Documents/projects/TourGuideApp/openaccess/MetObjects.csv')

relevant_columns = [
    'Title', 'Culture', 'Period', 'Dynasty', 'Reign',
    'Artist Display Name', 'Artist Nationality', 'Artist Display Bio',
    'Object Date', 'Medium', 'Dimensions', 'Credit Line',
    'City', 'Country', 'Region', 'Classification', 'Tags'
]

# Fill NaN values with empty strings to avoid errors during concatenation
data[relevant_columns] = data[relevant_columns].fillna('')

# Create a combined_text column with prioritized information
data['combined_text'] = data.apply(
    lambda row: ' | '.join([f"{col}: {row[col]}" for col in relevant_columns if row[col]]),
    axis=1
)

# Step 1: Retriever - TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(data['combined_text'])
joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump(tfidf_matrix, 'tfidf_matrix.pkl')
joblib.dump(data, 'data.pkl')