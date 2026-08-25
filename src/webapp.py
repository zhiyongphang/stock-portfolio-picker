from flask import Flask, request, redirect

from .brief import build_brief
from .dashboard import render_html
from .portfolio import add_holding, remove_holding

app = Flask(__name__)


@app.route("/")
def index():
    return render_html(build_brief(), interactive=True)


@app.route("/refresh", methods=["POST"])
def refresh():
    return redirect("/")


@app.route("/holdings/add", methods=["POST"])
def holdings_add():
    ticker = request.form["ticker"]
    shares = float(request.form["shares"])
    cost_basis_raw = request.form.get("cost_basis", "").strip()
    cost_basis = float(cost_basis_raw) if cost_basis_raw else None
    add_holding(ticker, shares, cost_basis)
    return redirect("/")


@app.route("/holdings/remove/<ticker>", methods=["POST"])
def holdings_remove(ticker):
    remove_holding(ticker)
    return redirect("/")


if __name__ == "__main__":
    app.run(port=5050, debug=False)
