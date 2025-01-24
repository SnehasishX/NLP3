from flask import Flask, render_template, request, jsonify
import yfinance as yf
import plotly.graph_objs as go

app = Flask(__name__)

# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.route("/")
def index():
    stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    return render_template("index.html", stocks=stocks)

@app.route("/update_chart")
def update_chart():
    symbol = request.args.get("symbol", "AAPL")
    chart_type = request.args.get("chartType", "candlestick")
    interval = request.args.get("interval", "1d")

    # Fetch data for the specified symbol and interval
    try:
        data = yf.Ticker(symbol).history(interval=interval, period="10y")
        if data.empty:
            return jsonify(error="No data available for the selected stock or interval.")
        data['RSI'] = calculate_rsi(data)
    except Exception as e:
        return jsonify(error=f"Error fetching data: {str(e)}")

    fig = go.Figure()

    # Main stock chart based on selected chart type
    if chart_type == "candlestick":
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
    elif chart_type == "line":
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name="Close Price"
        ))
    elif chart_type == "bar":
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Close'],
            name="Close Price"
        ))

    fig.update_layout(
        title=f"{symbol} Stock Chart ({interval} Interval)",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white"
    )

    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(
        x=data.index,
        y=data['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='blue')
    ))
    rsi_fig.update_layout(
        title="RSI Chart",
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        template="plotly_white"
    )

    return jsonify(chart=fig.to_json(), rsi=rsi_fig.to_json())

if __name__ == "__main__":
    app.run(debug=True)