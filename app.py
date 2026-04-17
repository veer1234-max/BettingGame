from flask import Flask, request, jsonify

app = Flask(__name__)

MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1

ROWS = 3
COLS = 3

symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}

symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2
}


def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []

    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)

    return winnings, winning_lines


def get_slot_machine_spin(rows, cols, symbols):
    import random

    all_symbols = []
    for symbol, count in symbols.items():
        for _ in range(count):
            all_symbols.append(symbol)

    columns = []
    for _ in range(cols):
        column = []
        current_symbols = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)
        columns.append(column)

    return columns


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python Betting Game</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                background: #f7f7f7;
            }
            .card {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }
            input, button {
                padding: 10px;
                margin: 8px 0;
                width: 100%;
                font-size: 16px;
            }
            button {
                background: black;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
            button:hover {
                opacity: 0.9;
            }
            .slot-grid {
                margin-top: 20px;
                font-size: 28px;
                text-align: center;
                line-height: 1.8;
                font-weight: bold;
            }
            .result {
                margin-top: 20px;
                font-size: 18px;
                white-space: pre-line;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎰 Python Betting Game</h1>
            <p>Enter your balance, number of lines, and bet per line.</p>

            <label>Balance</label>
            <input type="number" id="balance" min="1" value="100">

            <label>Lines (1-3)</label>
            <input type="number" id="lines" min="1" max="3" value="1">

            <label>Bet per line (1-100)</label>
            <input type="number" id="bet" min="1" max="100" value="10">

            <button onclick="spinGame()">Spin</button>

            <div class="slot-grid" id="slots"></div>
            <div class="result" id="result"></div>
        </div>

        <script>
            async function spinGame() {
                const balance = parseInt(document.getElementById("balance").value);
                const lines = parseInt(document.getElementById("lines").value);
                const bet = parseInt(document.getElementById("bet").value);

                const response = await fetch("/spin", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ balance, lines, bet })
                });

                const data = await response.json();

                if (data.error) {
                    document.getElementById("result").innerText = "Error: " + data.error;
                    document.getElementById("slots").innerHTML = "";
                    return;
                }

                const slots = data.slots;
                let display = "";

                for (let row = 0; row < slots[0].length; row++) {
                    let rowValues = [];
                    for (let col = 0; col < slots.length; col++) {
                        rowValues.push(slots[col][row]);
                    }
                    display += rowValues.join(" | ") + "<br>";
                }

                document.getElementById("slots").innerHTML = display;
                document.getElementById("result").innerText =
                    "Total Bet: $" + data.total_bet + "\\n" +
                    "Winnings: $" + data.winnings + "\\n" +
                    "Winning Lines: " + (data.winning_lines.length ? data.winning_lines.join(", ") : "None") + "\\n" +
                    "Net Result: $" + data.net_result + "\\n" +
                    "Remaining Balance: $" + data.remaining_balance;
            }
        </script>
    </body>
    </html>
    """


@app.route("/spin", methods=["POST"])
def spin():
    data = request.get_json()

    try:
        balance = int(data.get("balance", 0))
        lines = int(data.get("lines", 0))
        bet = int(data.get("bet", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input values."}), 400

    if balance <= 0:
        return jsonify({"error": "Balance must be greater than 0."}), 400

    if not (1 <= lines <= MAX_LINES):
        return jsonify({"error": f"Lines must be between 1 and {MAX_LINES}."}), 400

    if not (MIN_BET <= bet <= MAX_BET):
        return jsonify({"error": f"Bet must be between ${MIN_BET} and ${MAX_BET}."}), 400

    total_bet = bet * lines

    if total_bet > balance:
        return jsonify({"error": f"Not enough balance. Your current balance is ${balance}."}), 400

    slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
    winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
    net_result = winnings - total_bet
    remaining_balance = balance + net_result

    return jsonify({
        "slots": slots,
        "total_bet": total_bet,
        "winnings": winnings,
        "winning_lines": winning_lines,
        "net_result": net_result,
        "remaining_balance": remaining_balance
    })


if __name__ == "__main__":
    app.run(debug=True)