# Amazon Product Scraper

A simple Amazon product scraper to extract product details from Amazon.com using Python Requests and Beautifulsoup.

A simple amazon product detail scraper that crawls product information from the top 3 pages of search results based on search keywords, including ASIN `ASIN`, name `Name`， brand `Brand`, seller `Seller`， shipper `Shipper`， price `Price`, category `Category`, best sellers rank `BSR`, rating `Rating` , number of ratings `Ratings`, number of reviews `reviews` and link `link`, and exports the data as a csv file.

## Usage

From a terminal 

1. Clone this project  `git clone https://github.com/85Ryan/amazon-scraper.git` and cd into it `cd amazon-scraper`
2. Install Requirements `pip3 install -r requirements.txt`
3. Create a `.env` file in the root directory and add an environment variable named `COOKIE`, setting its value to your browser `cookie`.
4. Run `python main.py`
5. Get the data from `exports` folder

## Notes

Please follow the notes below when using this scraper:

1. Only use it for personal learning and research purposes.
2. Do not use it for commercial or illegal purposes.
3. Please comply with Amazon's terms and conditions of use.
4. Be mindful of privacy concerns and ensure that you do not scrape user personal data.

By using this scraper, you are deemed to have agreed to the above terms and conditions.