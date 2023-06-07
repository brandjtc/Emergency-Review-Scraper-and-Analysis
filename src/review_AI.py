import json
import gensim.downloader
import torch
from gensim.models import Word2Vec, KeyedVectors
from langdetect import detect
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

# Function to get the sentiment of a review text using a pre-trained DistilBERT model
def get_sentiment(review_text):
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')

    input_text = f"{review_text}"

    # Tokenize and encode the input text for the model
    inputs = tokenizer.encode_plus(
        input_text,
        return_tensors='pt',
        padding=True,
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)[0]

    # Get the predicted label and determine if it's positive or negative
    predicted_label = torch.argmax(outputs).item()
    labels = ['negative', 'positive']
    sentiment = labels[predicted_label]

    return sentiment

# Function to classify the review text based on dimensions and sub-dimensions defined in a prompt
def classify_data(review_text, prompt_json, word2vec_model):
    prompt = json.loads(prompt_json)

    dimensions = prompt["Dimensions"]
    dimension_scores = []

    for dimension in dimensions:
        dimension_name = dimension["Dimension"]
        sub_dimensions = dimension["Sub-Dimensions"]
        sub_dimension_scores = []

        for sub_dimension in sub_dimensions:
            sub_dimension_name = sub_dimension["Sub-Dimension"]
            definition = sub_dimension["Definition"]

            # Calls the function to perform the similarity calculation
            sub_dimension_score = calculate_similarity_score(review_text, definition, word2vec_model)
            sub_dimension_scores.append({
                "Sub-Dimension": sub_dimension_name,
                "Score": round(sub_dimension_score)
            })

        if sub_dimension_scores:
            # Calculate the average score of sub-dimensions within a dimension
            dimension_score = round(sum(sub['Score'] for sub in sub_dimension_scores) / len(sub_dimension_scores))
        else:
            dimension_score = 0

        dimension_scores.append({
            "Dimension": dimension_name,
            "Score": dimension_score,
            "Sub-Dimensions": sub_dimension_scores
        })

    return dimension_scores

# Function to calculate the similarity score between a review text and a definition
def calculate_similarity_score(review_text, definition, word2vec_model):
    review_tokens = review_text.lower().split()
    definition_tokens = definition.lower().split()

    review_vector = []
    definition_vector = []

    # Iterate over each token in the review text
    for token in review_tokens:
        if token in word2vec_model.key_to_index:
            # Add the word vector to the review vector if it's present in the Word2Vec model
            review_vector.append(word2vec_model[token])

    # Does the same now but for definition
    for token in definition_tokens:
        if token in word2vec_model.key_to_index:
            # Similarly, adds the word vector to the definition vector if it's present
            definition_vector.append(word2vec_model[token])

    if not review_vector or not definition_vector:
        return 0

    # Calculate the similarity score between the review and definition vectors
    similarity_score = word2vec_model.n_similarity(review_vector, definition_vector)
    return similarity_score * 100

def process_reviews(data, prompt_text, word2vec_model):
    output_data = []

    for item in data:
        review_text = item['review']

        dimension_scores = classify_data(review_text, prompt_text, word2vec_model)
        sentiment = get_sentiment(review_text)

        output = {
            'Review': review_text,
            'Sentiment': sentiment,
            'Dimensions': dimension_scores
        }

        output_data.append(output)

    return output_data

def main():
    # Read data from the JSON file
    with open(r'data\ReviewCollection.json', 'r') as file:
        data = json.load(file)

    # Read the JSON prompt from a separate file
    with open(r'data\dimension_data.json', 'r') as file:
        json_prompt = json.load(file)

    prompt_text = json.dumps(json_prompt)

    # Load the Word2Vec model
    word2vec_model = gensim.downloader.load('word2vec-google-news-300')

    # Process each review
    output_data = process_reviews(data, prompt_text, word2vec_model)

    # Write output to a file
    output_file = r'data\output.json'
    with open(output_file, 'w') as file:
        json.dump(output_data, file, indent=4)

    print(f'Processing completed! Output saved to {output_file}.')

if __name__ == "__main__":
    main()
