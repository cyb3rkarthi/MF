import re
import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from .email_service import dispatch_inquiry_email
from .project_images import enrich_project


main = Blueprint("main", __name__)

def is_valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email.strip()))

def get_iso_now():
    return datetime.now(timezone.utc).isoformat()

# =========================================================================
# Page Routes
# =========================================================================

@main.route("/")
def home():
    db = current_app.extensions["db"]
    projects = list(db.projects.find({}, {"_id": 0}).sort("order", 1))
    return render_template("home.html", projects=projects, featured_projects=projects[:3])

@main.route("/services")
def services():
    return render_template("services.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/projects")
def projects():
    category = request.args.get("category", "").strip()
    db = current_app.extensions["db"]

    query = {}
    if category and category.lower() != "all":
        query["category"] = category

    projects_list = list(db.projects.find(query, {"_id": 0}).sort("order", 1))

    # ── Image enrichment (reversible) ─────────────────────────────────────
    # Controlled by IMAGE_SELECTION_ENABLED in .env
    # If false/missing → grey placeholder (original behaviour)
    # MongoDB records are NEVER modified — enrichment is in-memory only
    images_enabled = os.getenv("IMAGE_SELECTION_ENABLED", "true").strip().lower() == "true"
    if images_enabled:
        projects_list = [enrich_project(p) for p in projects_list]
    # ─────────────────────────────────────────────────────────────────────

    return render_template(
        "projects.html",
        projects=projects_list,
        selected_category=category or "All",
        images_enabled=images_enabled,
    )


@main.route("/contact")
def contact():
    prefill_service = request.args.get("service", "").strip()
    active_tab = request.args.get("tab", "contact").strip()
    return render_template("contact.html", prefill_service=prefill_service, active_tab=active_tab)


# =========================================================================
# Form Submission APIs (clients, restaurants, contacts, reviews)
# =========================================================================

# 1. CLIENT DETAILS -> madras_foodies.clients
@main.post("/api/clients")
def submit_client():
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data submitted"}), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if not name:
        return jsonify({"success": False, "message": "Client name is required."}), 400
    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "A valid email address is required."}), 400

    now = get_iso_now()
    client_doc = dict(data)
    client_doc["name"] = name
    client_doc["email"] = email
    client_doc["phone"] = phone
    client_doc["created_at"] = now
    client_doc["updated_at"] = now

    db = current_app.extensions["db"]
    db.clients.insert_one(client_doc)

    # Email notification
    dispatch_inquiry_email({
        "name": name,
        "email": email,
        "phone": phone,
        "service": "Client Registration: " + str(data.get("service", "Consultancy Client")),
        "message": f"Client Details:\nName: {name}\nEmail: {email}\nPhone: {phone}\nCity/Location: {data.get('location', 'N/A')}\nNotes: {data.get('notes', data.get('message', 'N/A'))}",
        "created_at": now
    })

    if is_json:
        return jsonify({"success": True, "ok": True, "message": "Client details saved successfully"})
    flash("Client details saved successfully", "success")
    return redirect(url_for("main.contact", tab="client"))


# 2. RESTAURANT DETAILS -> madras_foodies.restaurants
@main.post("/api/restaurants")
def submit_restaurant():
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data submitted"}), 400

    restaurant_name = str(data.get("restaurant_name", "")).strip()
    owner_name = str(data.get("owner_name", data.get("name", ""))).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if not restaurant_name:
        return jsonify({"success": False, "message": "Restaurant name is required."}), 400
    if not owner_name:
        return jsonify({"success": False, "message": "Owner/Contact person name is required."}), 400
    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "A valid email address is required."}), 400

    now = get_iso_now()
    restaurant_doc = dict(data)
    restaurant_doc["restaurant_name"] = restaurant_name
    restaurant_doc["owner_name"] = owner_name
    restaurant_doc["email"] = email
    restaurant_doc["phone"] = phone
    restaurant_doc["created_at"] = now
    restaurant_doc["updated_at"] = now

    db = current_app.extensions["db"]
    db.restaurants.insert_one(restaurant_doc)

    # Email notification
    dispatch_inquiry_email({
        "name": f"{owner_name} ({restaurant_name})",
        "email": email,
        "phone": phone,
        "service": f"Restaurant Onboarding: {restaurant_name}",
        "message": f"Restaurant: {restaurant_name}\nOwner: {owner_name}\nLocation: {data.get('location', 'N/A')}\nCuisine: {data.get('cuisine_type', 'N/A')}\nSeating Capacity: {data.get('seating_capacity', 'N/A')}\nProject Stage: {data.get('project_stage', 'N/A')}\nDetails: {data.get('message', 'N/A')}",
        "created_at": now
    })

    if is_json:
        return jsonify({"success": True, "ok": True, "message": "Restaurant details saved successfully"})
    flash("Restaurant details saved successfully", "success")
    return redirect(url_for("main.contact", tab="restaurant"))


# 3. CONTACT FORM -> madras_foodies.contacts
@main.post("/api/contacts")
@main.post("/api/contact")
def submit_contact():
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data submitted"}), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    service = str(data.get("service", "")).strip() or "General Hospitality Consultancy"
    message = str(data.get("message", "")).strip()

    if not name:
        err = "Full name is required."
        return (jsonify({"success": False, "message": err}), 400) if is_json else (flash(err, "error"), redirect(url_for("main.contact")))[1]
    if not email or not is_valid_email(email):
        err = "Please provide a valid email address."
        return (jsonify({"success": False, "message": err}), 400) if is_json else (flash(err, "error"), redirect(url_for("main.contact")))[1]
    if not message:
        err = "Project details / message is required."
        return (jsonify({"success": False, "message": err}), 400) if is_json else (flash(err, "error"), redirect(url_for("main.contact")))[1]

    now = get_iso_now()
    contact_doc = dict(data)
    contact_doc["name"] = name
    contact_doc["email"] = email
    contact_doc["phone"] = phone
    contact_doc["service"] = service
    contact_doc["message"] = message
    contact_doc["created_at"] = now
    contact_doc["updated_at"] = now

    db = current_app.extensions["db"]
    db.contacts.insert_one(contact_doc)

    # Email notification
    dispatch_inquiry_email(contact_doc)

    success_msg = f"Thank you, {name}! Your enquiry has been received. Our team will contact you shortly."
    if is_json:
        return jsonify({"success": True, "ok": True, "message": success_msg})

    flash(success_msg, "success")
    return redirect(url_for("main.contact"))


# 4. REVIEWS -> madras_foodies.reviews
@main.post("/api/reviews")
def submit_review():
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data submitted"}), 400

    client_name = str(data.get("client_name", data.get("name", ""))).strip()
    restaurant_name = str(data.get("restaurant_name", "")).strip()
    review = str(data.get("review", data.get("message", ""))).strip()
    raw_rating = data.get("rating", 5)

    if not client_name:
        return jsonify({"success": False, "message": "Client name is required."}), 400
    if not review:
        return jsonify({"success": False, "message": "Review text is required."}), 400

    try:
        rating = float(raw_rating)
        if rating.is_integer():
            rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Rating must be a number between 1 and 5."}), 400

    now = get_iso_now()
    review_doc = dict(data)
    review_doc["client_name"] = client_name
    review_doc["restaurant_name"] = restaurant_name
    review_doc["rating"] = rating
    review_doc["review"] = review
    review_doc["created_at"] = now
    review_doc["updated_at"] = now

    db = current_app.extensions["db"]
    db.reviews.insert_one(review_doc)

    if is_json:
        return jsonify({"success": True, "ok": True, "message": "Review saved successfully. Thank you for your feedback!"})
    flash("Review saved successfully. Thank you!", "success")
    return redirect(url_for("main.home"))


# =========================================================================
# Status & Query APIs
# =========================================================================

@main.route("/api/status")
def status():
    db = current_app.extensions["db"]
    db_type = current_app.extensions.get("db_type", "unknown")

    def count_col(col):
        try:
            return col.count_documents({}) if hasattr(col, "count_documents") else len(list(col.find({})))
        except Exception:
            return 0

    return jsonify({
        "status": "healthy",
        "frontend": "connected",
        "backend": "Flask operational",
        "database": {
            "name": "madras_foodies",
            "engine": db_type,
            "connected": True,
            "collections": {
                "clients": count_col(db.clients),
                "restaurants": count_col(db.restaurants),
                "contacts": count_col(db.contacts),
                "reviews": count_col(db.reviews),
                "projects": count_col(db.projects)
            }
        }
    })

@main.route("/api/projects")
def api_projects():
    category = request.args.get("category", "").strip()
    db = current_app.extensions["db"]
    query = {}
    if category and category.lower() != "all":
        query["category"] = category
    projects_list = list(db.projects.find(query, {"_id": 0}).sort("order", 1))
    return jsonify({
        "success": True,
        "ok": True,
        "count": len(projects_list),
        "category": category or "All",
        "projects": projects_list
    })
