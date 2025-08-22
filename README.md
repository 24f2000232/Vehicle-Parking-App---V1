
# Vehicle Parking App - V1

A web-based vehicle parking management system built using Flask, SQLite, and Bootstrap.

## 📁 Project Structure

```
parking_app_24f2000232/
├── app.py
├── db_config.py
├── requirements.txt
├── project_report.pdf
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html
│   ├── admin_dashboard.html
│   ├── view_spots.html
│   ├── admin_view_spots.html
│   ├── reserve_form.html
│   ├── booking_history.html
│   ├── my_bookings.html
│   ├── edit_profile.html
│   ├── add_lot.html
│   ├── edit_lot.html
│   ├── view_users.html
│   └── release_confirm.html
├── models/
│   └── models.py
```

## 💡 Key Features

- **User Functionality:**
  - Register/Login
  - View available parking spots
  - Book and release spots
  - View booking history
  - Edit profile details

- **Admin Functionality:**
  - Add, edit, delete parking lots
  - View all spots with status indicators
  - View all registered users
  - Simple analytics with Chart.js

- **APIs:**
  - RESTful JSON responses for lots, spots, bookings, users, and history.

## 🚀 Technologies Used

- **Backend:** Flask, SQLAlchemy, Werkzeug
- **Frontend:** Bootstrap 5, Chart.js
- **Database:** SQLite

## ✅ How to Run Locally

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Set up the database.
3. Start the server:
   ```
   python app.py
   ```
4. Access via:
   ```
   http://localhost:5000
   ```

## ✍️ Author

**Name:** Sarang Gajanan Rao  
**Roll Number:** 24F2000232  
**Email:** 24f2000232@ds.study.iitm.ac.in


## 📄 Notes

AI tools (LLMs) were used for debugging, brainstorming, and learning frontend components while developing this project.
