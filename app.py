from flask import Flask, render_template, jsonify, request
from data.resorts import RESORTS, get_resort_by_id, get_powder_report
import random
import os

app = Flask(__name__)


@app.route("/")
def index():
    """Home page with the interactive map."""
    return render_template("index.html", resorts=RESORTS)


@app.route("/resort/<resort_id>")
def resort_detail(resort_id):
    """Resort detail page."""
    resort = get_resort_by_id(resort_id)
    if not resort:
        return "Resort not found", 404
    return render_template("resort.html", resort=resort)


@app.route("/compare")
def compare():
    """Resort comparison page."""
    ids = request.args.getlist("ids")
    resorts = [get_resort_by_id(r) for r in ids if get_resort_by_id(r)]
    return render_template("compare.html", resorts=resorts, all_resorts=RESORTS)


@app.route("/api/resorts")
def api_resorts():
    """API endpoint returning all resorts as JSON (for map rendering)."""
    return jsonify(RESORTS)


@app.route("/api/resort/<resort_id>")
def api_resort(resort_id):
    """API endpoint for a single resort."""
    resort = get_resort_by_id(resort_id)
    if not resort:
        return jsonify({"error": "Not found"}), 404
    return jsonify(resort)


@app.route("/api/powder")
def api_powder():
    """Powder radar - resorts with best fresh snow in last 24-48h."""
    return jsonify(get_powder_report())


@app.route("/api/filter")
def api_filter():
    """Filter resorts by various criteria."""
    min_snow = request.args.get("min_snow", 0, type=int)
    max_pass = request.args.get("max_pass", 9999, type=int)
    difficulty = request.args.get("difficulty", None)  # beginner / intermediate / expert
    family = request.args.get("family", None)
    luxury = request.args.get("luxury", None)
    freeride = request.args.get("freeride", None)
    country = request.args.get("country", None)

    results = RESORTS.copy()

    if min_snow > 0:
        results = [r for r in results if r["weather"]["snow_depth"] >= min_snow]

    if max_pass < 9999:
        results = [r for r in results if r["ski_pass"]["day"] <= max_pass]

    if difficulty == "beginner":
        results = [r for r in results if r["difficulty"]["green"] >= 15]
    elif difficulty == "intermediate":
        results = [r for r in results if r["difficulty"]["blue"] >= 35]
    elif difficulty == "expert":
        results = [r for r in results if r["difficulty"]["black"] >= 15]

    if family == "true":
        results = [r for r in results if r["family_friendly"]]

    if luxury == "true":
        results = [r for r in results if r["luxury"]]

    if freeride == "true":
        results = [r for r in results if "freeride" in r["tags"] or "off-piste" in r["tags"]]

    if country:
        results = [r for r in results if r["country"].lower() == country.lower()]

    return jsonify(results)


@app.route("/api/book", methods=["POST"])
def api_book():
    """Simulated booking endpoint."""
    data = request.get_json()
    booking_ref = f"LFT-{random.randint(10000, 99999)}"
    return jsonify({
        "success": True,
        "booking_ref": booking_ref,
        "message": f"Booking confirmed! Reference: {booking_ref}",
        "details": data
    })


if __name__ == "__main__":
    print("🏔️  LIFTLINE - Starting server...")
    print("🌐  Open http://127.0.0.1:5000 in your browser")
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)

