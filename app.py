
import os

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from dotenv import load_dotenv
from supabase import create_client, Client


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "helpconnect-dev-secret-key"
)


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing from .env")


# =========================================================
# CREATE SUPABASE CLIENT
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register")
def register():
    return render_template("register.html")


# =========================================================
# REGISTER API
# =========================================================

@app.route("/api/register", methods=["POST"])
def api_register():

    try:
        data = request.get_json(silent=True)

        if not data:
            return {
                "message": "Invalid request."
            }, 400

        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not full_name or not email or not password:
            return {
                "message": "Please fill in all fields."
            }, 400

        if len(password) < 6:
            return {
                "message": "Password must be at least 6 characters."
            }, 400

        # -----------------------------
        # CREATE SUPABASE ACCOUNT
        # -----------------------------

        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if not auth_response.user:
            return {
                "message": "Could not create account."
            }, 400

        return {
            "message": (
                "Account created successfully! "
                "Please check your email to confirm your account."
            )
        }, 201

    except Exception as e:

        print("REGISTER ERROR:", e)

        return {
            "message": str(e)
        }, 500


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login")
def login():
    return render_template("login.html")


# =========================================================
# LOGIN API
# =========================================================

@app.route("/api/login", methods=["POST"])
def api_login():

    try:
        data = request.get_json(silent=True)

        if not data:
            return {
                "message": "Invalid request."
            }, 400

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            return {
                "message": "Please enter your email and password."
            }, 400

        # -----------------------------
        # SUPABASE LOGIN
        # -----------------------------

        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return {
                "message": "Invalid email or password."
            }, 401

        # -----------------------------
        # SAVE USER SESSION
        # -----------------------------

        session["user_id"] = auth_response.user.id
        session["user_email"] = auth_response.user.email

        return {
            "message": "Login successful!"
        }, 200

    except Exception as e:

        print("LOGIN ERROR:", e)

        error_message = str(e)

        if "Email not confirmed" in error_message:
            return {
                "message": "Please confirm your email before logging in."
            }, 401

        return {
            "message": "Login failed. Please check your email and password."
        }, 401


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    try:

        response = (
            supabase
            .table("requests")
            .select("*")
            .eq("user_id", session["user_id"])
            .order("created_at", desc=True)
            .execute()
        )

        my_requests = response.data or []

        return render_template(
            "dashboard.html",
            user_email=session.get("user_email"),
            my_requests=my_requests
        )

    except Exception as e:

        print("DASHBOARD ERROR:", e)

        return render_template(
            "dashboard.html",
            user_email=session.get("user_email"),
            my_requests=[]
        )


# =========================================================
# ASK FOR HELP PAGE
# =========================================================
@app.route("/request-help")
def request_help():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("request_help.html")


# =========================================================
# CREATE HELP REQUEST API
# =========================================================

@app.route("/api/help-request", methods=["POST"])
def api_help_request():

    try:

        # -----------------------------
        # CHECK LOGIN
        # -----------------------------

        if "user_id" not in session:
            return {
                "message": "Please login before asking for help."
            }, 401

        data = request.get_json(silent=True)

        if not data:
            return {
                "message": "Invalid request."
            }, 400

        # -----------------------------
        # GET DATA
        # -----------------------------

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category", "").strip()
        location = data.get("location", "").strip()
        urgency = data.get("urgency", "normal").strip()

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not title:
            return {
                "message": "Please enter a title."
            }, 400

        if not description:
            return {
                "message": "Please enter a description."
            }, 400

        if not category:
            return {
                "message": "Please select a category."
            }, 400

        if not location:
            return {
                "message": "Please enter a location."
            }, 400

        # -----------------------------
        # INSERT REQUEST
        # -----------------------------

        response = (
            supabase
            .table("requests")
            .insert({
                "title": title,
                "description": description,
                "category": category,
                "location": location,
                "urgency": urgency,
                "status": "open",
                "user_id": session["user_id"]
            })
            .execute()
        )

        return {
            "message": "Help request posted successfully!",
            "data": response.data
        }, 201

    except Exception as e:

        print("HELP REQUEST ERROR:", e)

        return {
            "message": str(e)
        }, 500


# =========================================================
# REQUESTS PAGE
# =========================================================

@app.route("/requests")
def requests_page():

    try:

        response = (
            supabase
            .table("requests")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        requests_data = response.data or []

        print("REQUESTS DATA:", requests_data)

        return render_template(
            "requests.html",
            requests=requests_data
        )

    except Exception as e:

        print("REQUESTS ERROR:", e)

        return render_template(
            "requests.html",
            requests=[]
        )


# =========================================================
# VIEW OFFERS FOR MY REQUEST
# =========================================================

@app.route("/request/<request_id>/offers")
def request_offers(request_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    try:

        # -----------------------------
        # GET REQUEST
        # -----------------------------

        request_response = (
            supabase
            .table("requests")
            .select("*")
            .eq("id", request_id)
            .eq("user_id", session["user_id"])
            .execute()
        )

        if not request_response.data:
            return "Request not found or you do not have permission to view it.", 404

        help_request = request_response.data[0]

        # -----------------------------
        # GET OFFERS
        # -----------------------------

        offers_response = (
            supabase
            .table("responses")
            .select("*")
            .eq("request_id", request_id)
            .order("created_at", desc=True)
            .execute()
        )

        offers_data = offers_response.data or []

        return render_template(
            "request_offers.html",
            help_request=help_request,
            offers=offers_data
        )

    except Exception as e:

        print("REQUEST OFFERS ERROR:", e)

        return render_template(
            "request_offers.html",
            help_request=None,
            offers=[]
        )


# =========================================================
# OFFER HELP API
# =========================================================

@app.route("/api/offer-help", methods=["POST"])
def offer_help():

    try:

        # -----------------------------
        # CHECK LOGIN
        # -----------------------------

        if "user_id" not in session:
            return {
                "message": "Please login before offering help."
            }, 401

        data = request.get_json(silent=True)

        if not data:
            return {
                "message": "Invalid request."
            }, 400

        request_id = data.get("request_id")
        message = data.get("message", "").strip()

        if not request_id:
            return {
                "message": "Request ID is required."
            }, 400

        helper_id = session["user_id"]

        # -----------------------------
        # CHECK REQUEST EXISTS
        # -----------------------------

        request_response = (
            supabase
            .table("requests")
            .select("*")
            .eq("id", request_id)
            .execute()
        )

        if not request_response.data:
            return {
                "message": "Help request not found."
            }, 404

        help_request = request_response.data[0]

        # -----------------------------
        # DON'T OFFER ON OWN REQUEST
        # -----------------------------

        if help_request["user_id"] == helper_id:
            return {
                "message": "You cannot offer help on your own request."
            }, 400

        # -----------------------------
        # CHECK REQUEST STATUS
        # -----------------------------

        if help_request.get("status") != "open":
            return {
                "message": "This request is no longer open."
            }, 400

        # -----------------------------
        # CHECK EXISTING OFFER
        # -----------------------------

        existing_response = (
            supabase
            .table("responses")
            .select("*")
            .eq("request_id", request_id)
            .eq("helper_id", helper_id)
            .execute()
        )

        if existing_response.data:
            return {
                "message": "You have already offered help for this request."
            }, 400

        # -----------------------------
        # INSERT OFFER
        # -----------------------------

        response = (
            supabase
            .table("responses")
            .insert({
                "request_id": request_id,
                "helper_id": helper_id,
                "message": message,
                "status": "pending"
            })
            .execute()
        )

        return {
            "message": "Offer submitted successfully!",
            "data": response.data
        }, 201

    except Exception as e:

        print("OFFER HELP ERROR:", e)

        return {
            "message": str(e)
        }, 500



# =========================================================
# MY OFFERS PAGE
# =========================================================

@app.route("/offers")
def offers():

    if "user_id" not in session:
        return redirect(url_for("login"))

    try:

        # -------------------------------------------------
        # Get offers made by the logged-in helper
        # -------------------------------------------------

        response = (
            supabase
            .table("responses")
            .select("*")
            .eq(
                "helper_id",
                session["user_id"]
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        offers_data = response.data or []


        # -------------------------------------------------
        # Get the related request for every offer
        # -------------------------------------------------

        offers_with_requests = []

        for offer in offers_data:

            request_id = offer.get("request_id")

            help_request = None

            if request_id:

                request_response = (
                    supabase
                    .table("requests")
                    .select("*")
                    .eq(
                        "id",
                        request_id
                    )
                    .execute()
                )

                if request_response.data:

                    help_request = request_response.data[0]


            # Add request information to offer
            offer["help_request"] = help_request

            offers_with_requests.append(offer)


        print(
            "MY OFFERS:",
            offers_with_requests
        )


        return render_template(
            "offers.html",
            offers=offers_with_requests
        )


    except Exception as e:

        print(
            "OFFERS ERROR:",
            e
        )

        return render_template(
            "offers.html",
            offers=[]
        )



# =========================================================
# RESPOND TO OFFER
# ACCEPT / REJECT
# =========================================================

@app.route("/api/respond-to-offer", methods=["POST"])
def respond_to_offer():

    try:

        # -----------------------------
        # CHECK LOGIN
        # -----------------------------

        if "user_id" not in session:
            return {
                "message": "Please login first."
            }, 401

        data = request.get_json(silent=True)

        if not data:
            return {
                "message": "Invalid request."
            }, 400

        response_id = data.get("response_id")
        action = data.get("action")

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not response_id:
            return {
                "message": "Response ID is required."
            }, 400

        if action not in ["accepted", "rejected"]:
            return {
                "message": "Invalid action."
            }, 400

        # -----------------------------
        # FIND OFFER
        # -----------------------------

        offer_response = (
            supabase
            .table("responses")
            .select("*")
            .eq("id", response_id)
            .execute()
        )

        if not offer_response.data:
            return {
                "message": "Offer not found."
            }, 404

        offer = offer_response.data[0]

        request_id = offer["request_id"]

        # -----------------------------
        # FIND REQUEST
        # -----------------------------

        request_response = (
            supabase
            .table("requests")
            .select("*")
            .eq("id", request_id)
            .execute()
        )

        if not request_response.data:
            return {
                "message": "Help request not found."
            }, 404

        help_request = request_response.data[0]

        # -----------------------------
        # CHECK REQUEST OWNER
        # -----------------------------

        if help_request["user_id"] != session["user_id"]:
            return {
                "message": "You cannot manage this offer."
            }, 403

        # -----------------------------
        # UPDATE OFFER
        # -----------------------------

        (
            supabase
            .table("responses")
            .update({
                "status": action
            })
            .eq("id", response_id)
            .execute()
        )

        # -----------------------------
        # ACCEPTED
        # -----------------------------

        if action == "accepted":

            # Mark request as matched
            (
                supabase
                .table("requests")
                .update({
                    "status": "matched"
                })
                .eq("id", request_id)
                .execute()
            )

            # Optional:
            # Reject all other pending offers
            (
                supabase
                .table("responses")
                .update({
                    "status": "rejected"
                })
                .eq("request_id", request_id)
                .eq("status", "pending")
                .neq("id", response_id)
                .execute()
            )

            return {
                "message": "Offer accepted successfully!"
            }, 200

        # -----------------------------
        # REJECTED
        # -----------------------------

        return {
            "message": "Offer rejected successfully!"
        }, 200

    except Exception as e:

        print("RESPOND TO OFFER ERROR:", e)

        return {
            "message": str(e)
        }, 500


# =========================================================
# ACCEPT OFFER - DIRECT ROUTE
# =========================================================

@app.route("/api/offer/<offer_id>/accept", methods=["POST"])
def accept_offer(offer_id):

    if "user_id" not in session:
        return {
            "message": "Please login first."
        }, 401

    try:

        # -----------------------------
        # FIND OFFER
        # -----------------------------

        response = (
            supabase
            .table("responses")
            .select("*")
            .eq("id", offer_id)
            .execute()
        )

        if not response.data:
            return {
                "message": "Offer not found."
            }, 404

        offer = response.data[0]

        request_id = offer["request_id"]

        # -----------------------------
        # FIND REQUEST
        # -----------------------------

        request_response = (
            supabase
            .table("requests")
            .select("*")
            .eq("id", request_id)
            .execute()
        )

        if not request_response.data:
            return {
                "message": "Help request not found."
            }, 404

        help_request = request_response.data[0]

        # -----------------------------
        # CHECK OWNER
        # -----------------------------

        if help_request["user_id"] != session["user_id"]:
            return {
                "message": "You cannot accept this offer."
            }, 403

        # -----------------------------
        # ACCEPT OFFER
        # -----------------------------

        (
            supabase
            .table("responses")
            .update({
                "status": "accepted"
            })
            .eq("id", offer_id)
            .execute()
        )

        # -----------------------------
        # UPDATE REQUEST
        # -----------------------------

        (
            supabase
            .table("requests")
            .update({
                "status": "matched"
            })
            .eq("id", request_id)
            .execute()
        )

        # -----------------------------
        # REJECT OTHER PENDING OFFERS
        # -----------------------------

        (
            supabase
            .table("responses")
            .update({
                "status": "rejected"
            })
            .eq("request_id", request_id)
            .eq("status", "pending")
            .neq("id", offer_id)
            .execute()
        )

        return {
            "message": "Offer accepted successfully!"
        }, 200

    except Exception as e:

        print("ACCEPT OFFER ERROR:", e)

        return {
            "message": str(e)
        }, 500


# =========================================================
# REJECT OFFER - DIRECT ROUTE
# =========================================================

@app.route("/api/offer/<offer_id>/reject", methods=["POST"])
def reject_offer(offer_id):

    if "user_id" not in session:
        return {
            "message": "Please login first."
        }, 401

    try:

        # -----------------------------
        # FIND OFFER
        # -----------------------------

        response = (
            supabase
            .table("responses")
            .select("*")
            .eq("id", offer_id)
            .execute()
        )

        if not response.data:
            return {
                "message": "Offer not found."
            }, 404

        offer = response.data[0]

        request_id = offer["request_id"]

        # -----------------------------
        # FIND REQUEST
        # -----------------------------

        request_response = (
            supabase
            .table("requests")
            .select("*")
            .eq("id", request_id)
            .execute()
        )

        if not request_response.data:
            return {
                "message": "Help request not found."
            }, 404

        help_request = request_response.data[0]

        # -----------------------------
        # CHECK OWNER
        # -----------------------------

        if help_request["user_id"] != session["user_id"]:
            return {
                "message": "You cannot reject this offer."
            }, 403

        # -----------------------------
        # REJECT OFFER
        # -----------------------------

        (
            supabase
            .table("responses")
            .update({
                "status": "rejected"
            })
            .eq("id", offer_id)
            .execute()
        )

        return {
            "message": "Offer rejected successfully!"
        }, 200

    except Exception as e:

        print("REJECT OFFER ERROR:", e)

        return {
            "message": str(e)
        }, 500


# =========================================================
# TEST DATABASE
# =========================================================

@app.route("/test-db")
def test_db():

    try:

        # IMPORTANT:
        # Your application uses "requests",
        # not "help_requests".

        response = (
            supabase
            .table("requests")
            .select("*")
            .execute()
        )

        return {
            "status": "success",
            "message": "Supabase connection is working!",
            "data": response.data
        }

    except Exception as e:

        print("TEST DB ERROR:", e)

        return {
            "status": "error",
            "message": str(e)
        }, 500


# =========================================================
# RUN FLASK
# =========================================================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
