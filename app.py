from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
from datetime import datetime 

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_parking_app_v1' # Using a more specific key

DB_NAME = 'parking.db'

# -------------------- Database Setup --------------------
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Users table
        cur.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Parking Lots table
        cur.execute('''
            CREATE TABLE parking_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price_per_hour REAL NOT NULL,
                max_spots INTEGER NOT NULL,
                address TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                city TEXT NOT NULL             -- Added city column
            )
        ''')

        # Parking Spots table
        cur.execute('''
            CREATE TABLE parking_spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_id INTEGER,
                status TEXT DEFAULT 'A', -- 'A' for Available, 'O' for Occupied
                FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
            )
        ''')

        # Reservations
        cur.execute('''
            CREATE TABLE reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                spot_id INTEGER,
                in_time TEXT,
                out_time TEXT,
                cost REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (spot_id) REFERENCES parking_spots(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Database initialized.")
        print("Default Admin: Username 'admin', Password 'admin'")
    else:
        print("Database already exists.")

# Call init_db once when the application starts within app context
with app.app_context():
    init_db()

# -------------------- Routes --------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['user'] = 'admin'
            flash('Logged in as Admin.', 'success')
            return redirect(url_for('admin_dashboard'))
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session['user_id'] = user[0] # Store user_id in session
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('user') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Get parking lot details
    cur.execute("SELECT id, name, price_per_hour, max_spots, address, pin_code, city FROM parking_lots")
    parking_lots = cur.fetchall()

    # Get status of all parking spots for charts
    cur.execute("SELECT status, COUNT(*) FROM parking_spots GROUP BY status")
    spot_status_data = cur.fetchall()
    
    available_spots = 0
    occupied_spots = 0
    for status, count in spot_status_data:
        if status == 'A':
            available_spots = count
        elif status == 'O':
            occupied_spots = count

    # Get all users and their parking summaries
    cur.execute("""
        SELECT
            u.id,
            u.username,
            SUM(CASE WHEN r.out_time IS NOT NULL THEN 1 ELSE 0 END) AS total_parks,
            SUM(CASE WHEN r.out_time IS NOT NULL THEN r.cost ELSE 0 END) AS total_cost
        FROM
            users u
        LEFT JOIN
            reservations r ON u.id = r.user_id
        GROUP BY
            u.id, u.username
        ORDER BY
            u.username
    """)
    users_with_summary = cur.fetchall()

    conn.close()

    return render_template('admin_dashboard.html', 
                           parking_lots=parking_lots, 
                           available_spots=available_spots, 
                           occupied_spots=occupied_spots,
                           users=users_with_summary)

@app.route('/admin/user_details/<int:user_id>')
def admin_user_details(user_id):
    if session.get('user') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Get basic user info
    cur.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()

    if not user:
        flash('User not found.', 'danger')
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # Get all reservations for this user with lot and spot details
    cur.execute("""
        SELECT
            r.id AS reservation_id,
            pl.name AS lot_name,
            ps.id AS spot_id,
            r.in_time,
            r.out_time,
            r.cost
        FROM
            reservations r
        JOIN
            parking_spots ps ON r.spot_id = ps.id
        JOIN
            parking_lots pl ON ps.lot_id = pl.id
        WHERE
            r.user_id = ?
        ORDER BY
            r.in_time DESC
    """, (user_id,))
    user_reservations = cur.fetchall()

    # Calculate total parks and total cost for this specific user
    cur.execute("SELECT COUNT(id), SUM(cost) FROM reservations WHERE user_id = ? AND out_time IS NOT NULL", (user_id,))
    summary_data = cur.fetchone()
    total_parks = summary_data[0] if summary_data[0] else 0
    total_cost = summary_data[1] if summary_data[1] else 0

    conn.close()

    return render_template('admin_user_details.html',
                           user_info=user,
                           user_reservations=user_reservations,
                           total_parks=total_parks,
                           total_cost=total_cost)


@app.route('/user', methods=['GET', 'POST']) # Allow POST for pin code and city search
def user_dashboard():
    if 'user' not in session or session['user'] == 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    search_pin_code = request.form.get('pin_code')
    search_city = request.form.get('city')

    # Build the query for available parking lots based on pin code or city
    available_lots_query = """
        SELECT pl.id, pl.name, pl.price_per_hour, pl.address, pl.pin_code, pl.city,
               COUNT(ps.id) AS available_count
        FROM parking_lots pl
        JOIN parking_spots ps ON pl.id = ps.lot_id 
        WHERE ps.status = 'A' 
    """
    query_params = []
    
    # Add conditions based on search inputs
    if search_pin_code and search_city:
        available_lots_query += " AND (pl.pin_code = ? OR pl.city LIKE ?)"
        query_params.append(search_pin_code)
        query_params.append(f'%{search_city}%') # Use LIKE for partial city matches
    elif search_pin_code:
        available_lots_query += " AND pl.pin_code = ?"
        query_params.append(search_pin_code)
    elif search_city:
        available_lots_query += " AND pl.city LIKE ?"
        query_params.append(f'%{search_city}%') # Use LIKE for partial city matches

    available_lots_query += """
        GROUP BY pl.id, pl.name, pl.price_per_hour, pl.address, pl.pin_code, pl.city
        HAVING available_count > 0
        ORDER BY pl.name
    """
    cur.execute(available_lots_query, query_params)
    available_lots = cur.fetchall()

    # Get user's current reservation (if any)
    cur.execute("""
        SELECT r.id, pl.name, ps.id, r.in_time, r.out_time, r.cost, ps.status
        FROM reservations r
        JOIN parking_spots ps ON r.spot_id = ps.id
        JOIN parking_lots pl ON ps.lot_id = pl.id
        WHERE r.user_id = ? AND r.out_time IS NULL
    """, (user_id,))
    current_reservation = cur.fetchone()

    # Get user's parking history
    cur.execute("""
        SELECT r.id, pl.name, ps.id, r.in_time, r.out_time, r.cost
        FROM reservations r
        JOIN parking_spots ps ON r.spot_id = ps.id
        JOIN parking_lots pl ON ps.lot_id = pl.id
        WHERE r.user_id = ? AND r.out_time IS NOT NULL
        ORDER BY r.in_time DESC
    """, (user_id,))
    parking_history = cur.fetchall()

    # Get user's parking summary data for charts (total cost, total parking hours)
    cur.execute("""
        SELECT 
            SUM(cost), 
            SUM(CAST(julianday(out_time) - julianday(in_time) AS REAL) * 24)
        FROM reservations 
        WHERE user_id = ? AND out_time IS NOT NULL
    """, (user_id,))
    user_summary = cur.fetchone()
    total_cost = user_summary[0] if user_summary[0] else 0
    total_parking_hours = user_summary[1] if user_summary[1] else 0.0

    conn.close()

    return render_template('user_dashboard.html', 
                           username=session['user'],
                           available_lots=available_lots,
                           current_reservation=current_reservation,
                           parking_history=parking_history,
                           total_cost=total_cost,
                           total_parking_hours=total_parking_hours,
                           last_searched_pin_code=search_pin_code, # Pass back the searched pin code
                           last_searched_city=search_city) # Pass back the searched city


@app.route('/reserve_spot/<int:lot_id>', methods=['POST'])
def reserve_spot(lot_id):
    if 'user' not in session or session['user'] == 'admin':
        flash('Please log in to reserve a spot.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Check if user already has an active reservation
    cur.execute("SELECT * FROM reservations WHERE user_id = ? AND out_time IS NULL", (user_id,))
    if cur.fetchone():
        flash('You already have an active reservation. Please release your current spot first.', 'warning')
        conn.close()
        return redirect(url_for('user_dashboard'))

    # Find the first available spot in the chosen lot
    cur.execute("SELECT id FROM parking_spots WHERE lot_id = ? AND status = 'A' LIMIT 1", (lot_id,))
    spot = cur.fetchone()

    if spot:
        spot_id = spot[0]
        in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("UPDATE parking_spots SET status = 'O' WHERE id = ?", (spot_id,))
        cur.execute("INSERT INTO reservations (user_id, spot_id, in_time) VALUES (?, ?, ?)", (user_id, spot_id, in_time))
        conn.commit()
        flash(f'Parking spot {spot_id} in lot {lot_id} reserved successfully! Park your vehicle.', 'success')
    else:
        flash('No available spots in this lot.', 'danger')
    
    conn.close()
    return redirect(url_for('user_dashboard'))


@app.route('/release_spot/<int:reservation_id>', methods=['POST'])
def release_spot(reservation_id):
    if 'user' not in session or session['user'] == 'admin':
        flash('Please log in to release a spot.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Get reservation details
    cur.execute("SELECT spot_id, in_time FROM reservations WHERE id = ? AND user_id = ? AND out_time IS NULL", (reservation_id, user_id))
    reservation = cur.fetchone()

    if reservation:
        spot_id, in_time_str = reservation
        out_time = datetime.now()
        in_time = datetime.strptime(in_time_str, '%Y-%m-%d %H:%M:%S')
        
        duration_hours = (out_time - in_time).total_seconds() / 3600.0

        # Get price per hour from the parking lot
        cur.execute("""
            SELECT pl.price_per_hour FROM parking_lots pl
            JOIN parking_spots ps ON pl.id = ps.lot_id
            WHERE ps.id = ?
        """, (spot_id,))
        price_per_hour_row = cur.fetchone()
        
        if price_per_hour_row:
            price_per_hour = price_per_hour_row[0]
            cost = round(duration_hours * price_per_hour, 2)
        else:
            cost = 0.0 # Default if price not found, though it shouldn't happen if lot exists
            flash('Warning: Parking lot price not found, cost set to 0.', 'warning')


        cur.execute("UPDATE parking_spots SET status = 'A' WHERE id = ?", (spot_id,))
        cur.execute("UPDATE reservations SET out_time = ?, cost = ? WHERE id = ?", (out_time.strftime('%Y-%m-%d %H:%M:%S'), cost, reservation_id))
        conn.commit()
        flash(f'Parking spot released. Total cost: ₹{cost:.2f}', 'success')
    else:
        flash('Reservation not found or already released.', 'danger')
    
    conn.close()
    return redirect(url_for('user_dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_lot():
    if session.get('user') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        max_spots = int(request.form['max_spots'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        city = request.form['city'] # Get city from form

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        try:
            # Create parking lot - include city
            cur.execute("INSERT INTO parking_lots (name, price_per_hour, max_spots, address, pin_code, city) VALUES (?, ?, ?, ?, ?, ?)",
                        (name, price, max_spots, address, pin_code, city))
            lot_id = cur.lastrowid

            # Create spots
            for _ in range(max_spots):
                cur.execute("INSERT INTO parking_spots (lot_id, status) VALUES (?, 'A')", (lot_id,))

            conn.commit()
            flash(f'Parking Lot "{name}" created successfully with {max_spots} spots!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error creating parking lot: {e}', 'danger')
        finally:
            conn.close()
    return render_template('create_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if session.get('user') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_max_spots = int(request.form['max_spots'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        city = request.form['city'] # Get city from form

        cur.execute("SELECT max_spots FROM parking_lots WHERE id = ?", (lot_id,))
        old_max_spots = cur.fetchone()[0]

        try:
            # Update parking lot - include city
            cur.execute("UPDATE parking_lots SET name = ?, price_per_hour = ?, max_spots = ?, address = ?, pin_code = ?, city = ? WHERE id = ?",
                        (name, price, new_max_spots, address, pin_code, city, lot_id))

            # Adjust spots if max_spots changed
            if new_max_spots > old_max_spots:
                spots_to_add = new_max_spots - old_max_spots
                for _ in range(spots_to_add):
                    cur.execute("INSERT INTO parking_spots (lot_id, status) VALUES (?, 'A')", (lot_id,))
                flash(f'Added {spots_to_add} new spots to {name}.', 'info')
            elif new_max_spots < old_max_spots:
                cur.execute("SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = 'A'", (lot_id,))
                available_count = cur.fetchone()[0]
                
                spots_to_remove = old_max_spots - new_max_spots
                
                if spots_to_remove > available_count:
                    flash(f'Cannot decrease spots to {new_max_spots}. There are only {available_count} available spots. Please ensure enough spots are free before reducing capacity.', 'danger')
                    conn.rollback()
                    conn.close()
                    return redirect(url_for('edit_lot', lot_id=lot_id))
                
                cur.execute("DELETE FROM parking_spots WHERE id IN (SELECT id FROM parking_spots WHERE lot_id = ? AND status = 'A' LIMIT ?)", (lot_id, spots_to_remove))
                flash(f'Removed {spots_to_remove} spots from {name}.', 'info')

            conn.commit()
            flash(f'Parking Lot "{name}" updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating parking lot: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('admin_dashboard'))
    
    # GET request: Show current lot details - include city
    cur.execute("SELECT id, name, price_per_hour, max_spots, address, pin_code, city FROM parking_lots WHERE id = ?", (lot_id,))
    lot = cur.fetchone()
    conn.close()

    if not lot:
        flash('Parking Lot not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_lot.html', lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    if session.get('user') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = 'O'", (lot_id,))
    occupied_count = cur.fetchone()[0]

    if occupied_count > 0:
        flash(f'Cannot delete parking lot. There are {occupied_count} occupied spots. Release them first.', 'danger')
    else:
        try:
            cur.execute("DELETE FROM reservations WHERE spot_id IN (SELECT id FROM parking_spots WHERE lot_id = ?)", (lot_id,))
            cur.execute("DELETE FROM parking_spots WHERE lot_id = ?", (lot_id,))
            cur.execute("DELETE FROM parking_lots WHERE id = ?", (lot_id,))
            conn.commit()
            flash('Parking Lot and its spots deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting parking lot: {e}', 'danger')
            conn.rollback()
    
    conn.close()
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)