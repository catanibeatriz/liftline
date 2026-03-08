"""
LIFTLINE - Alpine Ski Resort Discovery & Booking Platform
==========================================================
A Flask web application that helps skiers and snowboarders
discover European ski resorts, check live conditions,
view ski maps, and book hotels, passes and equipment.

Authors: LIFTLINE Team
Course: Python Programming - Final Project
"""

from flask import Flask, render_template, jsonify, request
from data.resorts import RESORTS, get_resort_by_id, get_powder_report
import random
import os

app = Flask(__name__)


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def generate_booking_reference():
    """
    Generate a unique booking reference number.

    Parameters:
        None

    Returns:
        str: A booking reference string in the format 'LFT-XXXXX'
             where XXXXX is a random 5-digit number.
    """
    number = random.randint(10000, 99999)
    return f"LFT-{number}"


def filter_resorts_by_criteria(resorts, filters):
    """
    Filter a list of resorts based on given criteria.

    Parameters:
        resorts (list): A list of resort dictionaries to filter.
        filters (dict): A dictionary containing filter criteria:
            - min_snow (int): Minimum snow depth in cm.
            - max_pass (int): Maximum day pass price in euros.
            - difficulty (str): Skill level ('beginner', 'intermediate', 'expert').
            - family (str): 'true' to show only family-friendly resorts.
            - luxury (str): 'true' to show only luxury resorts.
            - freeride (str): 'true' to show only freeride resorts.
            - country (str): Country name to filter by.

    Returns:
        list: A filtered list of resort dictionaries matching all criteria.
    """
    results = resorts.copy()

    try:
        min_snow = int(filters.get("min_snow", 0))
        max_pass = int(filters.get("max_pass", 9999))
    except (ValueError, TypeError):
        min_snow = 0
        max_pass = 9999

    difficulty = filters.get("difficulty", None)
    family = filters.get("family", None)
    luxury = filters.get("luxury", None)
    freeride = filters.get("freeride", None)
    country = filters.get("country", None)

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

    return results


def validate_booking_data(data):
    """
    Validate incoming booking request data.

    Parameters:
        data (dict): The booking data from the request body.
                     Expected to contain a 'type' key at minimum.

    Returns:
        tuple: A tuple of (is_valid: bool, error_message: str).
               If valid, error_message will be an empty string.
    """
    if not data:
        return False, "No booking data provided."

    if "type" not in data:
        return False, "Booking type is required."

    valid_types = ["hotel", "ski_pass", "equipment"]
    if data["type"] not in valid_types:
        return False, f"Invalid booking type. Must be one of: {valid_types}"

    return True, ""


def get_resort_or_error(resort_id):
    """
    Retrieve a resort by its ID or return an error response.

    Parameters:
        resort_id (str): The unique identifier string for the resort
                         (e.g., 'zermatt', 'chamonix').

    Returns:
        tuple: A tuple of (resort: dict or None, error: dict or None).
               If found, error will be None.
               If not found, resort will be None and error will be a dict.
    """
    try:
        resort = get_resort_by_id(resort_id)
        if not resort:
            return None, {"error": f"Resort '{resort_id}' not found.", "status": 404}
        return resort, None
    except Exception as e:
        return None, {"error": f"An unexpected error occurred: {str(e)}", "status": 500}


# ─────────────────────────────────────────
# PAGE ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    """
    Render the homepage with the interactive map and resort grid.

    Parameters:
        None (uses Flask's request context)

    Returns:
        str: Rendered HTML of the index page with all resorts passed
             as template context.
    """
    try:
        return render_template("index.html", resorts=RESORTS)
    except Exception as e:
        return f"Error loading homepage: {str(e)}", 500


@app.route("/resort/<resort_id>")
def resort_detail(resort_id):
    """
    Render the detail page for a specific ski resort.

    Parameters:
        resort_id (str): The URL slug identifying the resort
                         (e.g., 'zermatt', 'st-moritz').

    Returns:
        str: Rendered HTML of the resort detail page,
             or a 404 error message if the resort is not found.
    """
    try:
        resort, error = get_resort_or_error(resort_id)
        if error:
            return f"Resort not found: {resort_id}", 404
        return render_template("resort.html", resort=resort)
    except Exception as e:
        return f"Error loading resort page: {str(e)}", 500


@app.route("/compare")
def compare():
    """
    Render the resort comparison page for up to 3 resorts side by side.

    Parameters:
        None (reads 'ids' query parameters from the URL,
              e.g. /compare?ids=zermatt&ids=chamonix)

    Returns:
        str: Rendered HTML of the comparison page with matched resorts
             and the full resort list for the selector dropdowns.
    """
    try:
        ids = request.args.getlist("ids")
        resorts = []
        for rid in ids:
            resort = get_resort_by_id(rid)
            if resort:
                resorts.append(resort)
        return render_template("compare.html", resorts=resorts, all_resorts=RESORTS)
    except Exception as e:
        return f"Error loading comparison page: {str(e)}", 500


# ─────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────

@app.route("/api/resorts")
def api_resorts():
    """
    API endpoint that returns all ski resorts as a JSON array.

    Parameters:
        None

    Returns:
        Response: A Flask JSON response containing a list of all
                  resort dictionaries with full data.
    """
    try:
        return jsonify(RESORTS)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resort/<resort_id>")
def api_resort(resort_id):
    """
    API endpoint that returns data for a single ski resort.

    Parameters:
        resort_id (str): The unique resort identifier in the URL path.

    Returns:
        Response: A Flask JSON response with the resort dictionary,
                  or a 404 JSON error if the resort is not found.
    """
    try:
        resort, error = get_resort_or_error(resort_id)
        if error:
            return jsonify({"error": error["error"]}), error["status"]
        return jsonify(resort)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/powder")
def api_powder():
    """
    API endpoint returning the Powder Radar — resorts ranked by
    fresh snowfall in the last 24 hours.

    Parameters:
        None

    Returns:
        Response: A Flask JSON response containing a list of powder
                  report dictionaries sorted by snowfall amount.
    """
    try:
        powder_data = get_powder_report()
        return jsonify(powder_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/filter")
def api_filter():
    """
    API endpoint that filters resorts based on query parameters.

    Parameters (via URL query string):
        min_snow (int): Minimum snow depth in cm (default: 0).
        max_pass (int): Maximum day pass price in euros (default: 9999).
        difficulty (str): Skill level filter ('beginner','intermediate','expert').
        family (str): 'true' to filter family-friendly resorts only.
        luxury (str): 'true' to filter luxury resorts only.
        freeride (str): 'true' to filter freeride terrain resorts only.
        country (str): Country name to filter by.

    Returns:
        Response: A Flask JSON response containing the filtered list
                  of resort dictionaries.
    """
    try:
        filters = {
            "min_snow":   request.args.get("min_snow", 0),
            "max_pass":   request.args.get("max_pass", 9999),
            "difficulty": request.args.get("difficulty", None),
            "family":     request.args.get("family", None),
            "luxury":     request.args.get("luxury", None),
            "freeride":   request.args.get("freeride", None),
            "country":    request.args.get("country", None),
        }
        results = filter_resorts_by_criteria(RESORTS, filters)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/book", methods=["POST"])
def api_book():
    """
    API endpoint to process a booking request (hotel, ski pass, or equipment).

    Parameters (via JSON request body):
        type (str): The type of booking — 'hotel', 'ski_pass', or 'equipment'.
        resort (str): The name of the resort being booked.
        Additional fields vary by booking type.

    Returns:
        Response: A Flask JSON response with booking confirmation including
                  a unique booking reference, or an error message if
                  the request data is invalid.
    """
    try:
        data = request.get_json()
        is_valid, error_message = validate_booking_data(data)

        if not is_valid:
            return jsonify({"success": False, "error": error_message}), 400

        booking_ref = generate_booking_reference()

        return jsonify({
            "success": True,
            "booking_ref": booking_ref,
            "message": f"Booking confirmed! Reference: {booking_ref}",
            "details": data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("🏔️  LIFTLINE - Starting server...")
    print("🌐  Open http://127.0.0.1:5000 in your browser")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)