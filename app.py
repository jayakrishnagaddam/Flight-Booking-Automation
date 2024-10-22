from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

app = Flask(__name__)

@app.route('/')
def automate_flight_booking():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    driver.get("https://www.goindigo.in/")
    
    title = driver.title
    url = driver.current_url
    print(f"Page Title: {title}")
    print(f"Page URL: {url}")
    
    expected_title = "Book Domestic and International Flights at Lowest Airfare"
    
    if title == expected_title:
        result = f"Successfully landed on the correct page!\nTitle: {title}\nURL: {url}"
    else:
        result = f"Incorrect page! Title: {title}\nURL: {url}"
    driver.quit()
    
    return result

if __name__ == '__main__':
    app.run(debug=True)
