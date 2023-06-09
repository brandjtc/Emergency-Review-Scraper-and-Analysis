# How to Scrape Google Play Reviews from Multiple Apps with Python and MongoDB

This guide will explain how to use the provided code to scrape Google Play reviews from multiple apps using Python and store the scraped data in MongoDB. The code utilizes the `google_play_scraper` library for retrieving app information and reviews, the `pymongo` library for interacting with the MongoDB database, and other supporting libraries.

## Prerequisites

Before getting started, make sure you have the following:

1. Python installed on your machine (version 3.6 or above).
2. An active internet connection.
3. A MongoDB instance set up and running.
4. An Excel file containing the app data, with a column named "Link to Google Play Store" containing the Google Play Store URLs of the apps.

## Step 1: Set Up Environment

1. Create a new directory for your project.
2. Open a terminal or command prompt and navigate to the project directory.
3. Create a new Python virtual environment by running the following command:

```
python3 -m venv myenv
```

4. Activate the virtual environment:

On Windows:
```
myenv\Scripts\activate.bat
```

On macOS/Linux:
```
source myenv/bin/activate
```

5. Install the required packages by running the following command:

```
pip install pandas re google_play_scraper pymongo openpyxl http.client dotenv tzlocal
```

## Step 2: Prepare the Excel File

1. Prepare an Excel file with the app data you want to scrape.
2. Add a sheet named "dataset" to the Excel file.
3. In the "dataset" sheet, add a column named "Link to Google Play Store" containing the Google Play Store URLs of the apps.
4. Save the Excel file in the project directory.

## Step 3: Set Up MongoDB

1. Install MongoDB on your machine if you haven't already.
2. Start the MongoDB service.
3. Create a new MongoDB database for storing the scraped data.
4. Make sure you have the connection details of your MongoDB instance, including the connection URI and the name of the database.

## Step 4: Modify the Code

Open a text editor and create a new Python file (e.g., `app_reviews_scraper.py`). Copy the provided code into the file.

1. Replace `os.getenv("EXCELFILEPATHGOOGLE")` with the path to your Excel file. For example, `"data/apps_data.xlsx"`.
2. Replace `os.getenv("MONGO_KEY")` with your MongoDB connection URI.
3. Replace `os.getenv("DATABASE")` with the name of your MongoDB database.
4. Replace `os.getenv("COLLECTION")` with the name of the MongoDB collection where you want to store the reviews.
5. Save the changes to the Python file.

## Step 5: Run the Scraper

1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Activate the Python virtual environment created earlier.
4. Run the following command to start scraping the reviews:

```
python app_reviews_scraper.py
```

The script will start scraping the reviews for each app in the Excel file and store the scraped data in the specified MongoDB collection.

## Understanding the Code

Here are some key blocks of code in the provided script and an explanation of how they work:

### Reading App Data from Excel

```python
excelFilePath = os.getenv("EXCELFILEPATHGOOGLE")
app_df = pd.read_excel(excelFilePath, sheet_name='dataset')
app_links = app_df['Link to Google Play Store'].tolist()
app_names = list(app_df['App-Name'])
```

This block of code reads the app data from the specified

Excel file. It assumes that the Excel file has a sheet named "dataset" and columns named "Link to Google Play Store" and "App-Name". It retrieves the app links and names and stores them in separate lists.

### Connecting to MongoDB

```python
client = MongoClient(os.getenv("MONGO_KEY"))
app_proj_db = client[os.getenv("DATABASE")]
review_collection = app_proj_db[os.getenv("COLLECTION")]
app_info_collection = app_proj_db[os.getenv("APPINFORMATION")]
```

This block of code connects to the MongoDB instance using the provided connection URI. It also specifies the database and collections to be used for storing the scraped data.

### Scraping Reviews for an App

```python
def scrape_reviews(app_info):
    # ...
```

This function is responsible for scraping the reviews for a single app. It takes an app_info tuple containing the app name and link as input.

The function first extracts the app ID from the Google Play Store URL. It then fetches the app information using the `app` function from the `google_play_scraper` library. The app information is printed and inserted into the `app_info_collection` in MongoDB.

The function then starts fetching the reviews for the app in batches. It handles network inconsistencies and retry logic to ensure all reviews are fetched. Each review is enhanced with additional information (app name, app ID, and platform) and stored in the `app_reviews` list.

After every 100 batches, the collected reviews are inserted into the `review_collection` in MongoDB. The progress is logged, and a sleep time is introduced between batches to avoid reaching any request limits imposed by the Google Play Store.

Once all reviews are fetched, the remaining reviews in `app_reviews` are inserted into the `review_collection`. The final progress is logged, and the total elapsed time is displayed.

### Running the Scraper

```python
if __name__ == '__main__':
    # ...

    pool = Pool(NUM_OF_PROCESSES)
    app_info_list = list(zip(app_names, app_links))
    results = pool.map(scrape_reviews, app_info_list)
    pool.close()
    pool.join()
    client.close()
```

This block of code is responsible for running the scraper. It creates a pool of processes using the `multiprocessing.Pool` class. The `scrape_reviews` function is then applied to each app_info tuple in `app_info_list` using the `map` method of the pool.

The pool of processes ensures that multiple apps are scraped simultaneously, speeding up the overall process. Once all apps are processed, the pool is closed, and the MongoDB connection is closed.

Note: Be sure to modify NUM_OF_PROCESSES with an amount you and your system is comfortable with (usually the same amount of cores a system has)

That's it! You have successfully set up and run the Google Play reviews scraper using Python and MongoDB. The scraped data is now stored in the specified MongoDB collection for further analysis or use.
