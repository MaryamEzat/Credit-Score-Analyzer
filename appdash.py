from dash import Dash, dcc, html, Input, Output, State
import mysql.connector
from datetime import datetime

app = Dash(__name__)
server = app.server

# Shared DB config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3308
}

def get_connection(database):
    return mysql.connector.connect(database=database, **db_config)

def get_user_info(user_id):
    with get_connection("users_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

def get_payment_data(user_id):
    with get_connection("payments_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT on_time_payments, total_payments FROM payment_records WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

def get_debt_data(user_id):
    with get_connection("debt_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT used_credit, credit_limit FROM debt_info WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

def get_history_data(user_id):
    with get_connection("history_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account_start_date FROM history_info WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

def get_mix_data(user_id):
    with get_connection("mix_reference_db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT types_used, total_types FROM credit_mix WHERE user_id = %s", (user_id,))
        return cursor.fetchone()

def calculate_score_components(user_id):
    payments = get_payment_data(user_id)
    debt = get_debt_data(user_id)
    history = get_history_data(user_id)
    mix = get_mix_data(user_id)

    payment_score = (payments[0] / payments[1]) * 100 if payments[1] else 0
    debt_score = (1 - (float(debt[0]) / float(debt[1]))) * 100 if debt[1] else 0
    account_age = datetime.now().year - history[0].year
    history_score = (account_age / 10) * 100
    mix_score = (mix[0] / mix[1]) * 100 if mix[1] else 0

    raw_score = (
        0.35 * payment_score +
        0.30 * debt_score +
        0.15 * history_score +
        0.20 * mix_score
    )
    scaled_score = 300 + ((raw_score / 100) * (850 - 300))

    return payment_score, debt_score, history_score, mix_score, scaled_score

# Layout
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap'
    ),

    html.Div([
        html.Div([
            html.Img(src="/assets/credit-score.png", height="40px", style={"marginRight": "10px"}),
            html.H1("Credit Score Analyzer", style={
                "fontSize": "32px",
                "fontWeight": "600",
                "margin": 0
            })
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "marginBottom": "30px"
        }),

        html.Div([
            dcc.Input(
                id="user-id",
                type="number",
                placeholder="Enter User ID",
                style={
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid #ccc",
                    "width": "220px",
                    "fontSize": "16px"
                }
            ),
            html.Button("Load Data", id="load-btn", n_clicks=0, style={
                "marginLeft": "12px",
                "padding": "10px 22px",
                "fontSize": "16px",
                "border": "none",
                "borderRadius": "6px",
                "backgroundColor": "#007bff",
                "color": "white",
                "cursor": "pointer"
            })
        ], style={"textAlign": "center", "marginBottom": "30px"}),

        dcc.Tabs(id="tabs", value='home', children=[
            dcc.Tab(label='🏠 Home', value='home'),
            dcc.Tab(label='📊 Payment History', value='payment'),
            dcc.Tab(label='💳 Debt Utilization', value='debt'),
            dcc.Tab(label='⏳ Credit History Age', value='history'),
            dcc.Tab(label='🔀 Credit Mix', value='mix'),
            dcc.Tab(label='✅ Final Score', value='score')
        ], style={
            "fontFamily": "Inter",
            "fontWeight": "500",
            "fontSize": "16px",
            "backgroundColor": "#ffffff"
        }),

        html.Div(id='tab-content', style={
            "padding": "30px",
            "backgroundColor": "#ffffff",
            "borderRadius": "10px",
            "margin": "30px auto",
            "maxWidth": "800px",
            "boxShadow": "0 4px 10px rgba(0,0,0,0.05)",
            "fontFamily": "Inter"
        })
    ])
], style={
    "backgroundColor": "#e9eff4",
    "minHeight": "100vh",
    "padding": "40px",
    "fontFamily": "Inter, sans-serif"
})

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    State('user-id', 'value')
)
def render_tab(tab, user_id):
    if not user_id:
        return html.Div("Please enter a user ID and click 'Load Data' first.", style={"color": "gray"})

    if tab == "home":
        user_info = get_user_info(user_id)
        if not user_info:
            return html.Div("❌ User not found.", style={"color": "red"})
        return html.Div([
            html.H4(f"User: {user_info[0]}"),
            html.P(f"Email: {user_info[1]}"),
            html.P("Proceed through each tab to load credit components."),
        ])
    
    elif tab == "payment":
        p = get_payment_data(user_id)
        score = (p[0] / p[1]) * 100 if p[1] else 0
        return html.Div([
            html.H4("📊 Payment History"),
            html.P(f"On-time payments: {p[0]}"),
            html.P(f"Total payments: {p[1]}"),
            html.H5(f"Score: {round(score, 2)} / 100")
        ])
    
    elif tab == "debt":
        d = get_debt_data(user_id)
        usage = float(d[0]) / float(d[1]) if d[1] else 1
        score = (1 - usage) * 100
        return html.Div([
            html.H4("💳 Debt Utilization"),
            html.P(f"Used Credit: {d[0]} EGP"),
            html.P(f"Credit Limit: {d[1]} EGP"),
            html.H5(f"Score: {round(score, 2)} / 100")
        ])
    
    elif tab == "history":
        h = get_history_data(user_id)
        age = datetime.now().year - h[0].year
        score = (age / 10) * 100
        return html.Div([
            html.H4("⏳ Credit History Age"),
            html.P(f"Account Started: {h[0]}"),
            html.P(f"Account Age: {age} years"),
            html.H5(f"Score: {round(score, 2)} / 100")
        ])
    
    elif tab == "mix":
        m = get_mix_data(user_id)
        score = (m[0] / m[1]) * 100 if m[1] else 0
        return html.Div([
            html.H4("🔀 Credit Mix"),
            html.P(f"Credit Types Used: {m[0]}"),
            html.P(f"Total Types Tracked: {m[1]}"),
            html.H5(f"Score: {round(score, 2)} / 100")
        ])
    
    elif tab == "score":
        p, d, h, m, total = calculate_score_components(user_id)
        return html.Div([
            html.H4("✅ Final Credit Score"),
            html.Ul([
                html.Li(f"📊 Payment History Score: {round(p, 2)}"),
                html.Li(f"💳 Debt Utilization Score: {round(d, 2)}"),
                html.Li(f"⏳ History Age Score: {round(h, 2)}"),
                html.Li(f"🔀 Credit Mix Score: {round(m, 2)}")
            ]),
            html.H3(f"Final iScore: {round(total, 2)} / 850", style={"marginTop": "20px", "color": "#28a745"})
        ])

    return html.Div("Invalid Tab")

if __name__ == "__main__":
    app.run(debug=True)