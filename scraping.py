# %%
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager
from  flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)
# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
   mars = mongo.db.mars
   mars_data = scraping.scrape_all()
   mars.update_one({}, {"$set":mars_data}, upsert=True)
   return redirect('/', code=302)



def scrape_all():
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    print(executable_path)
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []


    list_header_xpath = '//*[@id="product-section"]/div[2]/div/div/a'
    image_xpath = "(//div[@class='downloads']//a)[2]"
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    list_headers = browser.find_by_xpath(list_header_xpath)


    for header in list_headers:
       
        title =  header.text
        header.click()    
        browser.is_element_present_by_xpath(image_xpath, wait_time=3)
        
       
        full_image_elem = browser.find_by_xpath(image_xpath)[0]['href']
    
        hemisphere_image_urls.append({ "title": title, 
                            "url": full_image_elem})
    
        browser.back()

   

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "url": full_image_elem,
        "title": title,
        "image_urls": hemisphere_image_urls
        
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

   

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
            # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError: return None
    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url


def mars_facts():
 # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    def scrape():
    # Initiate headless driver for deployment
        executable_path = {'executable_path': ChromeDriverManager().install()}
        browser = Browser('chrome', **executable_path, headless=False)
        browser.visit(url)
        list_header_xpath = '//*[@id="product-section"]/div[2]/div/div/a'
        image_xpath = "(//div[@class='downloads']//a)[2]"
        # 3. Write code to retrieve the image urls and titles for each hemisphere.
        list_headers = browser.find_by_xpath(list_header_xpath)

        hemisphere_image_urls = []
        for header in list_headers:
            
            title =  header.text
            header.click()    
            browser.is_element_present_by_xpath(image_xpath, wait_time=3)
            full_image_elem = browser.find_by_xpath(image_xpath)[0]['href']
            
            hemisphere_image_urls.append({ "title": title, 
            "url": full_image_elem})
            
        browser.back()

        return
    # Add try/except for error handling
    try:
    # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException: 

        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']    
    df.set_index('Description', inplace=True)

# Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

# If running as script, print scraped data

    print(scrape_all())


