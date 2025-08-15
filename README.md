The **Vehicle Parking Management System** is a user-friendly web application built with Flask to simplify parking management. Whether you're a user reserving parking spots or an admin managing parking lots and users, this app has everything you need to make parking hassle-free.

---

## 🌟 What Can You Do?

### For Users:
- **Create an Account**: Register and securely log in to access your dashboard.
- **Reserve Parking Spots**: Easily find and reserve available parking spots.
- **Release Spots**: Free up your reserved spot when you're done.
- **Track Your History**: View your parking history, total sessions, and costs with interactive charts.

### For Administrators:
- **Manage Parking Lots**: Create, edit, or delete parking lots with ease.
- **View User Details**: Access user parking history and summaries.
- **Analyze Data**: Use dynamic charts to monitor parking spot usage.
- **Quick Actions**: Perform administrative tasks with just a few clicks.

> 🛡️ **Admin Login Credentials**  
> - **Username**: `admin`  
> - **Password**: `admin`

---

## 📂 How the Project is Organized

Here’s a quick overview of the project structure:

```

vehicle_parking_app
├── app.py               # Main Flask application file
├── parking.db           # SQLite database (auto-created)
├── templates/           # HTML templates for the app
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── create_lot.html
│   ├── edit_lot.html
│   └── admin_user_details.html
├── static/              # Static files (CSS, JS, images)
│   └── style.css
└── README.md            # Documentation

```

## Tech Stack

- **Flask**: Backend framework for routing and handling requests.
- **SQLite3**: Lightweight database for storing and retrieving data.
- **Bootstrap**: Responsive design for a user-friendly interface.
````
---

````
## 🛠 How to Use the App

### For Users:

1. **Register**: Create an account on the registration page.
2. **Log In**: Access your dashboard by logging in.
3. **Reserve a Spot**: Choose an available parking lot and reserve a spot.
4. **Release a Spot**: Free up your reserved spot when you're done.
5. **View History**: Check your parking history and summary.

### For Administrators:

1. **Log In**: Use the following credentials to access the admin dashboard:

   * **Username**: `admin`
   * **Password**: `admin`
2. **Manage Parking Lots**: Create, edit, or delete parking lots.
3. **View Users**: Access user details.
4. **Analyze Data**: Use the interactive chart to monitor parking spot usage.

---

## 📊 Cool Features

* **Interactive Charts**: Visualize parking spot availability and usage with dynamic charts.
* **Responsive Design**: The app works seamlessly on all devices, from desktops to smartphones.
* **Quick Actions**: Perform administrative tasks quickly and efficiently.

---
## 🚀 Getting Started

Follow these steps to set up and run the app on your local machine:

### 1️⃣ Clone the Repository
First, download the project files:

cd vehicle_parking_app
````

### 2️⃣ Install Dependencies

Make sure you have Python installed. Then, install the required libraries:
bash
pip install Flask
````

### 3️⃣ Run the Application

Start the Flask server:

bash
python app.py


### 4️⃣ Open the App

Open your browser and go to:

````
http://127.0.0.1:5000

````

## 📝 License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute it as per the license terms.

---

## 🤝 Want to Contribute?

We’d love your help to make this app even better! Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

Thank you for using the **Vehicle Parking App**! 🚗✨
