from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import calendar
from pymongo import MongoClient


app = Flask(__name__)

app.secret_key = 'your_secret_key'

# MongoDB connection URI
MONGO_URI = "mongodb+srv://hello1234:hello1234@cluster0.u5acte4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database('hellomotto')
holidays_collection = db.holidays
users_collection = db.users

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return 'Username already exists'

        # Insert the new user into the database
        user_data = {
            'username': username,
            'password': password,
            'holidays': []  # Initialize an empty list to store holiday data
        }
        users_collection.insert_one(user_data)

        session['username'] = username  # Store the username in the session
        return redirect(url_for('index'))  # Redirect to the index route

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username  # Store the username in the session
            return redirect(url_for('index'))  # Redirect to the index route
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
      # Get the current month and year
      current_month = datetime.datetime.now().month
      current_year = datetime.datetime.now().year
  
      # Get the calendar for the current month
      cal = calendar.monthcalendar(current_year, current_month)
  
      # list of dictionaries representing the dates and days
      holidays = []
  
      for week in cal:
          for day in week:
              if day != 0:
                  date = datetime.date(current_year, current_month, day)
                  weekday = date.weekday()
                  india_holiday = "No"
                  canada_holiday = "No"
                  us_holiday = "No"
  
                  # Saturdays and Sundays as holidays
                  if weekday == 5 or weekday == 6:
                      india_holiday = "Yes"
                      canada_holiday = "Yes"
                      us_holiday = "Yes"
  
                  # Fetch data from MongoDB for the current date
                  holiday_data = holidays_collection.find_one({"date": date.strftime("%Y-%m-%d")})
  
                  is_shift_allowance_applicable = ""
                  shift_timings = ""
  
                  if holiday_data:
                      is_shift_allowance_applicable = holiday_data.get("is_shift_allowance_applicable", "")
                      shift_timings = holiday_data.get("shift_timings", "")
  
                  holidays.append({
                      "date": date.strftime("%Y-%m-%d"),
                      "day": date.strftime("%A"),
                      "india_holiday": india_holiday,
                      "canada_holiday": canada_holiday,
                      "us_holiday": us_holiday,
                      "is_shift_allowance_applicable": is_shift_allowance_applicable,
                      "shift_timings": shift_timings
                  })
  
      if request.method == 'POST':
          for holiday in holidays:
              date_str = holiday['date']
              is_shift_allowance = request.form.get(f'is_shift_allowance_applicable_{date_str}', '')
              shift_timings = request.form.get(f'shift_timings_{date_str}', '')
  
              # Save data to MongoDB
              holiday_data = {
                  "date": date_str,
                  "day": holiday['day'],
                  "india_holiday": holiday['india_holiday'],
                  "canada_holiday": holiday['canada_holiday'],
                  "us_holiday": holiday['us_holiday'],
                  "is_shift_allowance_applicable": is_shift_allowance,
                  "shift_timings": shift_timings
              }
  
              holidays_collection.update_one(
                  {"date": date_str},
                  {"$set": holiday_data},
                  upsert=True
              )
  
              print(f"Date: {date_str}")
              print(f"Is Shift Allowance Applicable: {is_shift_allowance}")
              print(f"Shift Timings: {shift_timings}")
  
      return render_template('index.html', holidays=holidays)
    
    return render_template('signup.html', login_url=url_for('login'))
  
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True, host='0.0.0.0', port=8080)