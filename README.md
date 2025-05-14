# 💳 Credit Score Analyzer

A Dash web app that connects to distributed MySQL databases to calculate and display credit scores using real-time user data.

---

## 📊 Features

- Real-time score calculation
- Fetches data from 5 separate MySQL databases:
  - Payment history
  - Credit usage
  - Account age
  - Credit mix
  - User info
- Clean and interactive dashboard interface using Plotly Dash
- Simple and minimal local setup

---

## 🧱 Database Schema

The app expects the following tables to exist in separate databases, each queried independently:

### `users_db`
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255)
);
```

### `payments_db`
```sql
CREATE TABLE payment_records (
    user_id INT,
    on_time_payments INT,
    total_payments INT
);
```

### `debt_db`
```sql
CREATE TABLE debt_info (
    user_id INT,
    used_credit DECIMAL(10,2),
    credit_limit DECIMAL(10,2)
);
```

### `history_db`
```sql
CREATE TABLE history_info (
    user_id INT,
    account_start_date DATE
);
```

### `mix_reference_db`
```sql
CREATE TABLE credit_mix (
    user_id INT,
    types_used INT,
    total_types INT
);
```

---

## 🛠 Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/MaryamEzat/Credit-Score-Analyzer.git
cd Credit-Score-Analyzer
```

2. Install the required Python packages:

```bash
pip install dash mysql-connector-python
```

3. Start your MySQL server (on port `3308`) and ensure all 5 databases are set up.

4. Run the app:

```bash
python app.py
```

Then open your browser and go to:  
[http://localhost:8050](http://localhost:8050)

---

## 🧠 Credits

Built by **Maryam Hesham** for the **Distributed Data Analysis** project  
Faculty of Computers and Data Science, Alexandria University.
