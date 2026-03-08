"""
LIFTLINE Console - Alpine Ski Resort Discovery Platform
========================================================
A pure Python terminal application that allows users to
discover European ski resorts, check snow conditions,
filter by preferences, compare resorts, and simulate bookings.

Authors: LIFTLINE Team
Course: Python Programming - Final Project
"""

from data.resorts import RESORTS, get_resort_by_id, get_powder_report
import random
import time


# ─────────────────────────────────────────
# DISPLAY HELPER FUNCTIONS
# ─────────────────────────────────────────

def print_header():
    """
    Print the LIFTLINE welcome banner to the console.

    Parameters:
        None

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("        ❄  L I F T L I N E  ❄")
    print("     Your Alpine Ski Concierge")
    print("=" * 60)
    print("  Discover · Compare · Book · Ski")
    print("=" * 60 + "\n")


def print_divider():
    """
    Print a simple divider line to separate sections.

    Parameters:
        None

    Returns:
        None
    """
    print("\n" + "-" * 60 + "\n")


def print_resort_summary(resort):
    """
    Print a short summary card for a single resort.

    Parameters:
        resort (dict): A resort dictionary containing name, country,
                       region, slopes_km, lifts, weather, and ski_pass data.

    Returns:
        None
    """
    try:
        snow = resort["weather"]["snow_depth"]
        temp = resort["weather"]["temp"]
        day_pass = resort["ski_pass"]["day"]

        print(f"  🏔  {resort['name']} ({resort['country']})")
        print(f"      Region    : {resort['region']}")
        print(f"      Slopes    : {resort['slopes_km']} km  |  Lifts: {resort['lifts']}")
        print(f"      Snow      : {snow} cm  |  Temp: {temp}°C")
        print(f"      Day Pass  : €{day_pass}")
        print(f"      Tags      : {', '.join(resort['tags'][:3])}")
    except KeyError as e:
        print(f"  ⚠️  Missing data for resort: {e}")


def print_resort_detail(resort):
    """
    Print a full detailed view of a single resort including
    weather, difficulty breakdown, and hotel options.

    Parameters:
        resort (dict): A resort dictionary with complete data.

    Returns:
        None
    """
    try:
        print_divider()
        print(f"  {'='*50}")
        print(f"  🏔  {resort['name'].upper()}")
        print(f"  {'='*50}")
        print(f"  📍 {resort['region']}, {resort['country']}")
        print(f"  📝 {resort['description']}")
        print()

        # Stats
        print(f"  📊 RESORT STATS")
        print(f"     Peak Elevation : {resort['elevation_peak']}m")
        print(f"     Base Elevation : {resort['elevation_base']}m")
        print(f"     Vertical Drop  : {resort['elevation_peak'] - resort['elevation_base']}m")
        print(f"     Total Slopes   : {resort['slopes_km']} km")
        print(f"     Number of Lifts: {resort['lifts']}")
        print()

        # Difficulty
        d = resort["difficulty"]
        print(f"  🎿 DIFFICULTY BREAKDOWN")
        print(f"     🟢 Green  (Easy)        : {d['green']}%")
        print(f"     🔵 Blue   (Intermediate): {d['blue']}%")
        print(f"     🔴 Red    (Advanced)    : {d['red']}%")
        print(f"     ⚫ Black  (Expert)      : {d['black']}%")
        print()

        # Weather
        w = resort["weather"]
        print(f"  🌨  LIVE CONDITIONS")
        print(f"     Temperature   : {w['temp']}°C")
        print(f"     Snow Depth    : {w['snow_depth']} cm")
        print(f"     Forecast Snow : {w['forecast_snow']} cm")
        print(f"     Wind Speed    : {w['wind']} km/h")
        print(f"     Visibility    : {w['visibility']} km")
        print()

        # Ski Passes
        p = resort["ski_pass"]
        print(f"  🎟  SKI PASSES")
        print(f"     Day Pass     : €{p['day']}")
        print(f"     3-Day Pass   : €{p['multiday_3']}")
        print(f"     Season Pass  : €{p['season']}")
        print()

        # Hotels
        print(f"  🏨  NEARBY HOTELS")
        for hotel in resort["hotels"]:
            print(f"     • {hotel['name']}")
            print(f"       €{hotel['price']}/night  |  ⭐ {hotel['rating']}  |  🚡 {hotel['distance_lifts']} to lifts")
        print()

        # Tags
        print(f"  🏷  TAGS: {', '.join(resort['tags'])}")
        print(f"  👨‍👩‍👧 Family Friendly: {'Yes ✅' if resort['family_friendly'] else 'No'}")
        print(f"  ✨ Luxury Resort  : {'Yes ✅' if resort['luxury'] else 'No'}")
        print(f"  🌐 Official Site  : {resort['official_url']}")
        print_divider()

    except KeyError as e:
        print(f"  ⚠️  Error displaying resort details: missing field {e}")


# ─────────────────────────────────────────
# CORE FEATURE FUNCTIONS
# ─────────────────────────────────────────

def list_all_resorts():
    """
    Display a summary list of all available ski resorts.

    Parameters:
        None

    Returns:
        None
    """
    print_divider()
    print(f"  🌍 ALL RESORTS ({len(RESORTS)} total)\n")
    for i, resort in enumerate(RESORTS, 1):
        print(f"  [{i:02d}] ", end="")
        print_resort_summary(resort)
        print()


def search_resort_by_name():
    """
    Allow the user to search for a resort by typing its name.
    Performs a case-insensitive partial match search.

    Parameters:
        None (reads user input from the console)

    Returns:
        None
    """
    try:
        query = input("  🔍 Enter resort name to search: ").strip().lower()
        if not query:
            print("  ⚠️  Please enter a search term.")
            return

        results = [r for r in RESORTS if query in r["name"].lower()
                   or query in r["country"].lower()
                   or query in r["region"].lower()]

        if not results:
            print(f"  ❌ No resorts found matching '{query}'")
            return

        print(f"\n  Found {len(results)} result(s):\n")
        for resort in results:
            print_resort_summary(resort)
            print()

        if len(results) == 1:
            show = input("  View full details? (y/n): ").strip().lower()
            if show == "y":
                print_resort_detail(results[0])

    except Exception as e:
        print(f"  ⚠️  Search error: {e}")


def filter_resorts():
    """
    Filter resorts interactively based on user-selected criteria
    including country, difficulty, snow depth, pass price,
    and special flags like family-friendly or luxury.

    Parameters:
        None (reads user input from the console)

    Returns:
        list: A filtered list of resort dictionaries matching
              the user's chosen criteria.
    """
    print_divider()
    print("  🎿 FILTER RESORTS\n")

    results = RESORTS.copy()

    try:
        # Country filter
        countries = sorted(set(r["country"] for r in RESORTS))
        print("  Available countries: " + ", ".join(countries))
        country = input("  Filter by country (or press Enter to skip): ").strip()
        if country:
            results = [r for r in results if r["country"].lower() == country.lower()]

        # Difficulty filter
        print("\n  Difficulty: beginner / intermediate / expert")
        difficulty = input("  Filter by difficulty (or press Enter to skip): ").strip().lower()
        if difficulty == "beginner":
            results = [r for r in results if r["difficulty"]["green"] >= 15]
        elif difficulty == "intermediate":
            results = [r for r in results if r["difficulty"]["blue"] >= 35]
        elif difficulty == "expert":
            results = [r for r in results if r["difficulty"]["black"] >= 15]

        # Snow depth filter
        min_snow_input = input("\n  Minimum snow depth in cm (or press Enter to skip): ").strip()
        if min_snow_input:
            min_snow = int(min_snow_input)
            results = [r for r in results if r["weather"]["snow_depth"] >= min_snow]

        # Max day pass filter
        max_pass_input = input("  Maximum day pass price in € (or press Enter to skip): ").strip()
        if max_pass_input:
            max_pass = int(max_pass_input)
            results = [r for r in results if r["ski_pass"]["day"] <= max_pass]

        # Family friendly
        family = input("\n  Family friendly only? (y/n or Enter to skip): ").strip().lower()
        if family == "y":
            results = [r for r in results if r["family_friendly"]]

        # Luxury
        luxury = input("  Luxury resorts only? (y/n or Enter to skip): ").strip().lower()
        if luxury == "y":
            results = [r for r in results if r["luxury"]]

        # Freeride
        freeride = input("  Freeride terrain only? (y/n or Enter to skip): ").strip().lower()
        if freeride == "y":
            results = [r for r in results if "freeride" in r["tags"] or "off-piste" in r["tags"]]

        print_divider()

        if not results:
            print("  ❌ No resorts match your filters. Try again with different criteria.")
        else:
            print(f"  ✅ {len(results)} resort(s) found:\n")
            for resort in results:
                print_resort_summary(resort)
                print()

        return results

    except ValueError:
        print("  ⚠️  Invalid input. Please enter numbers where required.")
        return []
    except Exception as e:
        print(f"  ⚠️  Filter error: {e}")
        return []


def powder_radar():
    """
    Display the Powder Radar — a ranked list of resorts
    with the best fresh snowfall in the last 24 hours.

    Parameters:
        None

    Returns:
        None
    """
    try:
        print_divider()
        print("  ❄  POWDER RADAR — Best Snow Right Now\n")
        data = get_powder_report()

        if not data:
            print("  ⚠️  No powder data available.")
            return

        for i, p in enumerate(data, 1):
            print(f"  #{i}  {p['name']} ({p['country']})")
            print(f"       Snowfall last 24h : {p['snowfall_24h']} cm")
            print(f"       Snowfall last 48h : {p['snowfall_48h']} cm")
            print(f"       Powder Quality    : {p['powder_quality']}")
            print(f"       Wind              : {p['wind']}")
            print()

    except Exception as e:
        print(f"  ⚠️  Error loading powder radar: {e}")


def compare_resorts():
    """
    Allow the user to compare two resorts side by side,
    showing key metrics and automatically highlighting
    the better value for each category.

    Parameters:
        None (reads user input from the console)

    Returns:
        None
    """
    try:
        print_divider()
        print("  📊 COMPARE RESORTS\n")

        name1 = input("  Enter first resort name: ").strip().lower()
        name2 = input("  Enter second resort name: ").strip().lower()

        r1 = next((r for r in RESORTS if name1 in r["name"].lower()), None)
        r2 = next((r for r in RESORTS if name2 in r["name"].lower()), None)

        if not r1:
            print(f"  ❌ Could not find resort matching '{name1}'")
            return
        if not r2:
            print(f"  ❌ Could not find resort matching '{name2}'")
            return

        print_divider()
        print(f"  {'METRIC':<25} {r1['name']:<25} {r2['name']:<25}")
        print(f"  {'-'*75}")

        def compare_row(label, val1, val2, higher_is_better=True):
            """
            Print one comparison row, highlighting the better value.

            Parameters:
                label (str): The name of the metric being compared.
                val1: The value for resort 1.
                val2: The value for resort 2.
                higher_is_better (bool): True if a higher value is better.

            Returns:
                None
            """
            try:
                if higher_is_better:
                    mark1 = "✅" if val1 > val2 else "  "
                    mark2 = "✅" if val2 > val1 else "  "
                else:
                    mark1 = "✅" if val1 < val2 else "  "
                    mark2 = "✅" if val2 < val1 else "  "
                print(f"  {label:<25} {str(val1)+' '+mark1:<25} {str(val2)+' '+mark2:<25}")
            except Exception:
                print(f"  {label:<25} {str(val1):<25} {str(val2):<25}")

        compare_row("Peak Elevation (m)", r1["elevation_peak"], r2["elevation_peak"])
        compare_row("Slopes (km)", r1["slopes_km"], r2["slopes_km"])
        compare_row("Number of Lifts", r1["lifts"], r2["lifts"])
        compare_row("Snow Depth (cm)", r1["weather"]["snow_depth"], r2["weather"]["snow_depth"])
        compare_row("Day Pass (€)", r1["ski_pass"]["day"], r2["ski_pass"]["day"], higher_is_better=False)
        compare_row("Season Pass (€)", r1["ski_pass"]["season"], r2["ski_pass"]["season"], higher_is_better=False)
        compare_row("Black Runs (%)", r1["difficulty"]["black"], r2["difficulty"]["black"])
        compare_row("Green Runs (%)", r1["difficulty"]["green"], r2["difficulty"]["green"])

        print(f"\n  Family Friendly : {'Yes' if r1['family_friendly'] else 'No':<24} {'Yes' if r2['family_friendly'] else 'No'}")
        print(f"  Luxury Resort   : {'Yes' if r1['luxury'] else 'No':<24} {'Yes' if r2['luxury'] else 'No'}")
        print_divider()

    except Exception as e:
        print(f"  ⚠️  Comparison error: {e}")


def book_resort():
    """
    Simulate a full booking flow for a resort including
    hotel selection, ski pass purchase, and equipment rental.
    Generates a unique booking reference upon confirmation.

    Parameters:
        None (reads user input from the console)

    Returns:
        None
    """
    try:
        print_divider()
        print("  🎫 BOOK YOUR TRIP\n")

        name = input("  Enter resort name: ").strip().lower()
        resort = next((r for r in RESORTS if name in r["name"].lower()), None)

        if not resort:
            print(f"  ❌ Resort not found. Try again.")
            return

        print(f"\n  ✅ Booking for: {resort['name']}\n")

        # Hotel selection
        print("  🏨 Available Hotels:")
        for i, hotel in enumerate(resort["hotels"], 1):
            print(f"     [{i}] {hotel['name']} — €{hotel['price']}/night ⭐{hotel['rating']}")

        hotel_choice = input("\n  Select hotel number (or Enter to skip): ").strip()
        selected_hotel = None
        if hotel_choice.isdigit():
            idx = int(hotel_choice) - 1
            if 0 <= idx < len(resort["hotels"]):
                selected_hotel = resort["hotels"][idx]
                print(f"  ✅ Hotel selected: {selected_hotel['name']}")

        # Ski pass
        print(f"\n  🎟  Ski Passes:")
        print(f"     [1] Day Pass     — €{resort['ski_pass']['day']}")
        print(f"     [2] 3-Day Pass   — €{resort['ski_pass']['multiday_3']}")
        print(f"     [3] Season Pass  — €{resort['ski_pass']['season']}")

        pass_choice = input("\n  Select pass number (or Enter to skip): ").strip()
        pass_types = {
            "1": ("Day Pass", resort["ski_pass"]["day"]),
            "2": ("3-Day Pass", resort["ski_pass"]["multiday_3"]),
            "3": ("Season Pass", resort["ski_pass"]["season"]),
        }
        selected_pass = None
        if pass_choice in pass_types:
            selected_pass = pass_types[pass_choice]
            print(f"  ✅ Pass selected: {selected_pass[0]} — €{selected_pass[1]}")

        # Equipment
        print(f"\n  🎿 Equipment Rental:")
        equipment_options = ["Skis (€35/day)", "Snowboard (€38/day)", "Boots (€22/day)", "Helmet (€12/day)", "Jacket (€28/day)"]
        for i, item in enumerate(equipment_options, 1):
            print(f"     [{i}] {item}")

        equip_input = input("\n  Select equipment numbers separated by commas (or Enter to skip): ").strip()
        selected_equipment = []
        if equip_input:
            for num in equip_input.split(","):
                num = num.strip()
                if num.isdigit():
                    idx = int(num) - 1
                    if 0 <= idx < len(equipment_options):
                        selected_equipment.append(equipment_options[idx])

        # Summary & confirmation
        print_divider()
        print("  📋 BOOKING SUMMARY")
        print(f"     Resort  : {resort['name']}, {resort['country']}")
        if selected_hotel:
            print(f"     Hotel   : {selected_hotel['name']} — €{selected_hotel['price']}/night")
        if selected_pass:
            print(f"     Pass    : {selected_pass[0]} — €{selected_pass[1]}")
        if selected_equipment:
            print(f"     Gear    : {', '.join(selected_equipment)}")

        confirm = input("\n  Confirm booking? (y/n): ").strip().lower()
        if confirm == "y":
            ref = f"LFT-{random.randint(10000, 99999)}"
            print(f"\n  🎉 BOOKING CONFIRMED!")
            print(f"  📌 Your reference number: {ref}")
            print(f"  ✉️  A confirmation would be sent to your email.")
        else:
            print("  ❌ Booking cancelled.")

        print_divider()

    except ValueError:
        print("  ⚠️  Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"  ⚠️  Booking error: {e}")


# ─────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────

def main_menu():
    """
    Display the main menu and handle user navigation
    through all LIFTLINE features in a loop until
    the user chooses to exit.

    Parameters:
        None

    Returns:
        None
    """
    print_header()

    while True:
        try:
            print("  MAIN MENU")
            print("  ─────────────────────────────")
            print("  [1]  Browse All Resorts")
            print("  [2]  Search Resort by Name")
            print("  [3]  Filter Resorts")
            print("  [4]  ❄ Powder Radar")
            print("  [5]  Compare Two Resorts")
            print("  [6]  Book a Resort")
            print("  [0]  Exit")
            print("  ─────────────────────────────")

            choice = input("  Choose an option: ").strip()

            if choice == "1":
                list_all_resorts()
            elif choice == "2":
                search_resort_by_name()
            elif choice == "3":
                filter_resorts()
            elif choice == "4":
                powder_radar()
            elif choice == "5":
                compare_resorts()
            elif choice == "6":
                book_resort()
            elif choice == "0":
                print("\n  ❄ Thanks for using LIFTLINE. See you on the slopes! ⛷\n")
                break
            else:
                print("  ⚠️  Invalid option. Please choose 0-6.\n")

        except KeyboardInterrupt:
            print("\n\n  ❄ Goodbye! See you on the slopes! ⛷\n")
            break
        except Exception as e:
            print(f"  ⚠️  Unexpected error: {e}")


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    main_menu()