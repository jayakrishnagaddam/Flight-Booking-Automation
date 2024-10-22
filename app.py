# app.py
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from pymongo import MongoClient
import json

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb+srv://2100090162:manigaddam@deepsheild.kzgpo9p.mongodb.net/flight_booking")
db = client.flight_booking
users_collection = db.users
bookings_collection = db.bookings

class FlightBooker:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        self.driver = webdriver.Chrome(options=options)
        
    def book_flight(self, passenger_details):
        try:
            self.setup_driver()
            self.driver.get("https://www.goindigo.in/")
            
            # Verify landing
            assert "IndiGo" in self.driver.title
            print(f"URL: {self.driver.current_url}")
            print(f"Title: {self.driver.title}")
            
            # Click Book option
            book_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-dropdown='book']"))
            )
            book_btn.click()
            
            # Select Flight option
            flight_opt = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Flight"))
            )
            flight_opt.click()
            
            # Set passengers
            pax_btn = self.driver.find_element(By.CSS_SELECTOR, ".pax-dropdown")
            pax_btn.click()
            
            adult_plus = self.driver.find_element(By.CSS_SELECTOR, ".adult-plus")
            adult_plus.click()
            
            done_btn = self.driver.find_element(By.CSS_SELECTOR, ".done-button")
            done_btn.click()
            
            # Set locations
            from_input = self.driver.find_element(By.ID, "from-city")
            from_input.send_keys("Hyderabad")
            hyd_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-city='HYD']"))
            )
            hyd_option.click()
            
            to_input = self.driver.find_element(By.ID, "to-city")
            to_input.send_keys("Delhi")
            del_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-city='DEL']"))
            )
            del_option.click()
            
            # Set date (1 month from now)
            future_date = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
            date_input = self.driver.find_element(By.ID, "travel-date")
            self.driver.execute_script(f"arguments[0].value = '{future_date}'", date_input)
            
            # Search and select flight
            search_btn = self.driver.find_element(By.ID, "search-flight")
            search_btn.click()
            
            first_flight = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".flight-select-button"))
            )
            first_flight.click()
            
            next_btn = self.driver.find_element(By.CSS_SELECTOR, ".next-button")
            next_btn.click()
            
            # Fill passenger details
            self.fill_passenger_details(passenger_details)
            
            return {"status": "success", "message": "Flight booked successfully"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        finally:
            if self.driver:
                self.driver.quit()
                
    def fill_passenger_details(self, details):
        # Select gender
        gender_select = self.driver.find_element(By.NAME, "gender")
        gender_select.click()
        male_option = self.driver.find_element(By.CSS_SELECTOR, "[value='MALE']")
        male_option.click()
        
        # Fill name
        firstname = self.driver.find_element(By.NAME, "firstName")
        firstname.send_keys(details['firstName'])
        
        lastname = self.driver.find_element(By.NAME, "lastName")
        lastname.send_keys(details['lastName'])
        
        # Fill DOB
        dob_input = self.driver.find_element(By.NAME, "dob")
        self.driver.execute_script(f"arguments[0].value = '{details['dob']}'", dob_input)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    data = request.get_json()
    
    # Save to MongoDB
    booking_id = bookings_collection.insert_one(data).inserted_id
    
    # Initialize booker and perform booking
    booker = FlightBooker()
    result = booker.book_flight(data)
    
    if result["status"] == "success":
        bookings_collection.update_one(
            {"_id": booking_id},
            {"$set": {"status": "completed"}}
        )
    else:
        bookings_collection.update_one(
            {"_id": booking_id},
            {"$set": {"status": "failed", "error": result["message"]}}
        )
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)