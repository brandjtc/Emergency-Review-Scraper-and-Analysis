# Emergency-Review-Scraper-and-Analysis
A python program that uses libraries to scrape reviews off of IOS & Google Play Store apps and then publish them to a MongoDB database.
&nbsp;
&nbsp;
&nbsp;
&nbsp;
### Folder Directory
- **src:** Contains python scripts required to run the scrapers and the scraper accessories. Also houses the generated files subfolder that holds all of the programatically generated data reports.
- **data:** Contains the excel sheets used for the IOS and Google Play Scrapers to function, as well as the definitions and outputs of the AI sentiment analysis scripts.
- **guides:** Contains guides for getting started with setting up a MongoDB connection to store app reviews.

### This github repository is a joined effort between Brandon Catalano, who managed the IOS app store integration and data visualization primarily, Anthony Parra, responsible for the Google Play Store integration, and Dr. Bonaretti, the project lead, at Nova Southeastern University.
### It contains several scripts for scraping and storing google and IOS application reviews in Python, processing and analyzing data stored within a MongoDB database, and generating sentiment analysis using AI models.   
&nbsp; 

## Repository Table of Contents 
#### [How to Scrape and Store IOS Reviews from Multiple Apps with Python and MongoDB](https://github.com/brandjtc/Emergency-Review-Scraper-and-Analysis/blob/main/guide/ios_scraper_guide.md)
#### [How to Scrape and Store Google Play Store Reviews from Multiple Apps with Python and MongoDB](https://github.com/brandjtc/Emergency-Review-Scraper-and-Analysis/blob/main/guide/google_play_scraper_guide.md)
#### [Open AI Analysis Example Outputs](https://github.com/brandjtc/Emergency-Review-Scraper-and-Analysis/tree/main/src/Generated%20Files/Reviews)

# New Addition: Semantic Similarity Analysis
### semanticSimilarity.ipynb

This Jupyter notebook is designed to calculate semantic similarity between different sets of text data, using pre-trained BERT models and Sentence Transformers. The key features of the notebook include:

    Embeddings Calculation: It uses BERT to obtain embeddings for text data, including various dimensions related to emergency notifications and user reviews from different datasets.
    Cosine Similarity: It calculates the cosine similarity between the dimensions and the user-provided sentences to understand the semantic closeness.
    Data Visualization: The notebook includes functions to visualize the similarity scores and correlations between different dimensions using histograms and heatmaps.
    Data Analysis: It processes datasets such as reviews from the EmergencyReviewDB and Netflix descriptions, allowing for comparative analysis based on semantic similarity.

How to Use:

    Load Data: Ensure the necessary datasets, like EmergencyReviewDB.Filtered Reviews.csv and netflix_titles.csv, are uploaded in the environment.
    Run Notebook: Follow the provided code blocks to compute similarity matrices, visualize the data, and analyze the results.
    Output Analysis: Export the resulting similarity matrices and selected reviews based on similarity thresholds.

This notebook is a comprehensive tool for understanding the semantic aspects of emergency notifications and similar content, providing valuable insights into user perceptions and application functionalities.
