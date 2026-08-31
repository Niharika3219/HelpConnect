
// ==========================================
// HELPConnect JavaScript
// ==========================================

console.log("HelpConnect JavaScript loaded!");


// ==========================================
// LOGIN
// ==========================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const emailElement = document.getElementById("email");
        const passwordElement = document.getElementById("password");

        const email = emailElement ? emailElement.value.trim() : "";
        const password = passwordElement ? passwordElement.value : "";

        if (!email || !password) {
            alert("Please enter your email and password.");
            return;
        }

        try {

            const response = await fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const result = await response.json();

            alert(result.message);

            if (response.ok) {
                window.location.href = "/dashboard";
            }

        } catch (error) {

            console.error("Login error:", error);

            alert("Something went wrong. Please try again.");

        }

    });

}


// ==========================================
// REGISTER
// ==========================================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const fullNameElement = document.getElementById("full_name");
        const emailElement = document.getElementById("registerEmail");
        const passwordElement = document.getElementById("registerPassword");

        const fullName = fullNameElement
            ? fullNameElement.value.trim()
            : "";

        const email = emailElement
            ? emailElement.value.trim()
            : "";

        const password = passwordElement
            ? passwordElement.value
            : "";

        if (!fullName || !email || !password) {
            alert("Please fill in all fields.");
            return;
        }

        try {

            const response = await fetch("/api/register", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });

            const result = await response.json();

            alert(result.message);

            if (response.ok) {
                window.location.href = "/login";
            }

        } catch (error) {

            console.error("Registration error:", error);

            alert("Something went wrong. Please try again.");

        }

    });

}


// ==========================================
// CREATE HELP REQUEST
// ==========================================

const helpRequestForm =
    document.getElementById("helpRequestForm");

if (helpRequestForm) {

    helpRequestForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const titleElement =
                document.getElementById("title");

            const descriptionElement =
                document.getElementById("description");

            const categoryElement =
                document.getElementById("category");

            const locationElement =
                document.getElementById("location");

            const messageElement =
                document.getElementById("requestMessage");


            const title = titleElement
                ? titleElement.value.trim()
                : "";

            const description = descriptionElement
                ? descriptionElement.value.trim()
                : "";

            const category = categoryElement
                ? categoryElement.value
                : "";

            const location = locationElement
                ? locationElement.value.trim()
                : "";


            if (!title) {
                if (messageElement) {
                    messageElement.textContent =
                        "Please enter a title.";
                }
                return;
            }


            if (!description) {
                if (messageElement) {
                    messageElement.textContent =
                        "Please enter a description.";
                }
                return;
            }


            if (!category) {
                if (messageElement) {
                    messageElement.textContent =
                        "Please select a category.";
                }
                return;
            }


            if (!location) {
                if (messageElement) {
                    messageElement.textContent =
                        "Please enter a location.";
                }
                return;
            }


            try {

                const response = await fetch(
                    "/api/help-request",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            title: title,
                            description: description,
                            category: category,
                            location: location
                        })
                    }
                );


                const result = await response.json();


                if (messageElement) {
                    messageElement.textContent =
                        result.message;
                } else {
                    alert(result.message);
                }


                if (response.ok) {
                    helpRequestForm.reset();
                }

            } catch (error) {

                console.error(
                    "Help request error:",
                    error
                );

                if (messageElement) {
                    messageElement.textContent =
                        "Something went wrong.";
                } else {
                    alert("Something went wrong.");
                }

            }

        }
    );

}


// ==========================================
// OFFER HELP
// ==========================================
//
// Used on requests.html
//
// HTML:
// data-request-id="{{ item.id }}"
//
// API:
// POST /api/offer-help
//
// Sends:
// {
//     request_id: "...",
//     message: "..."
// }
//
// ==========================================

const offerButtons =
    document.querySelectorAll(".offer-help-btn");


offerButtons.forEach(function (button) {

    button.addEventListener(
        "click",
        async function () {

            const requestId =
                button.dataset.requestId;


            console.log(
                "OFFER HELP CLICKED"
            );

            console.log(
                "Request ID:",
                requestId
            );


            if (!requestId) {

                alert(
                    "Request ID is missing."
                );

                return;
            }


            // ----------------------------------
            // Confirm
            // ----------------------------------

            const confirmed = confirm(
                "Do you want to offer help for this request?"
            );


            if (!confirmed) {
                return;
            }


            // ----------------------------------
            // Ask for message
            // ----------------------------------

            const message = prompt(
                "Write a short message to the person who needs help:"
            );


            if (message === null) {
                return;
            }


            const finalMessage =
                message.trim() ||
                "I would like to help with this request.";


            // ----------------------------------
            // Disable button
            // ----------------------------------

            button.disabled = true;

            button.textContent =
                "Offering...";


            try {

                const response = await fetch(
                    "/api/offer-help",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            request_id: requestId,
                            message: finalMessage
                        })
                    }
                );


                const result =
                    await response.json();


                console.log(
                    "Offer response:",
                    result
                );


                if (response.ok) {

                    alert(
                        result.message ||
                        "Offer sent successfully!"
                    );

                    button.textContent =
                        "Offer Sent";

                } else {

                    alert(
                        result.message ||
                        "Could not send offer."
                    );

                    button.disabled = false;

                    button.textContent =
                        "Offer Help";

                }

            } catch (error) {

                console.error(
                    "Offer Help Error:",
                    error
                );

                alert(
                    "Something went wrong while offering help."
                );

                button.disabled = false;

                button.textContent =
                    "Offer Help";

            }

        }
    );

});


// ==========================================
// ACCEPT OFFER
// ==========================================
//
// API:
// POST /api/offer/<offer_id>/accept
//
// ==========================================

async function acceptOffer(offerId, button = null) {

    console.log(
        "ACCEPT OFFER:",
        offerId
    );


    const confirmed = confirm(
        "Are you sure you want to accept this offer?"
    );


    if (!confirmed) {
        return;
    }


    if (button) {

        button.disabled = true;

        button.textContent =
            "Accepting...";

    }


    try {

        const response = await fetch(
            "/api/offer/" +
            offerId +
            "/accept",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                }
            }
        );


        const result =
            await response.json();


        console.log(
            "Accept response:",
            result
        );


        alert(
            result.message ||
            "Offer accepted."
        );


        if (response.ok) {

            window.location.reload();

        } else {

            if (button) {

                button.disabled = false;

                button.textContent =
                    "Accept";

            }

        }

    } catch (error) {

        console.error(
            "Accept offer error:",
            error
        );

        alert(
            "Something went wrong while accepting the offer."
        );


        if (button) {

            button.disabled = false;

            button.textContent =
                "Accept";

        }

    }

}


// ==========================================
// REJECT OFFER
// ==========================================
//
// API:
// POST /api/offer/<offer_id>/reject
//
// ==========================================

async function rejectOffer(offerId, button = null) {

    console.log(
        "REJECT OFFER:",
        offerId
    );


    const confirmed = confirm(
        "Are you sure you want to reject this offer?"
    );


    if (!confirmed) {
        return;
    }


    if (button) {

        button.disabled = true;

        button.textContent =
            "Rejecting...";

    }


    try {

        const response = await fetch(
            "/api/offer/" +
            offerId +
            "/reject",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                }
            }
        );


        const result =
            await response.json();


        console.log(
            "Reject response:",
            result
        );


        alert(
            result.message ||
            "Offer rejected."
        );


        if (response.ok) {

            window.location.reload();

        } else {

            if (button) {

                button.disabled = false;

                button.textContent =
                    "Reject";

            }

        }

    } catch (error) {

        console.error(
            "Reject offer error:",
            error
        );

        alert(
            "Something went wrong while rejecting the offer."
        );


        if (button) {

            button.disabled = false;

            button.textContent =
                "Reject";

        }

    }

}


// ==========================================
// ACCEPT / REJECT USING GENERIC API
// ==========================================
//
// This function is available if another HTML
// page uses:
//
// respondToOffer(id, "accepted")
// respondToOffer(id, "rejected")
//
// ==========================================

async function respondToOffer(
    responseId,
    action
) {

    console.log(
        "RESPOND TO OFFER"
    );

    console.log(
        "Response ID:",
        responseId
    );

    console.log(
        "Action:",
        action
    );


    if (!responseId) {

        alert(
            "Response ID is missing."
        );

        return;
    }


    if (
        action !== "accepted" &&
        action !== "rejected"
    ) {

        alert(
            "Invalid offer action."
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/respond-to-offer",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    response_id: responseId,
                    action: action
                })
            }
        );


        const result =
            await response.json();


        alert(
            result.message
        );


        if (response.ok) {

            window.location.reload();

        }

    } catch (error) {

        console.error(
            "Respond to offer error:",
            error
        );

        alert(
            "Something went wrong. Please try again."
        );

    }

}


console.log(
    "HelpConnect JavaScript ready!"
);
