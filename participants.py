# A dictionary of dictionaries where key is the participant's name and the value their data, which must at least
# contain an email address
PARTICIPANTS = {
    "Rudolph": {
        # Always required
        "email": "Rudolph@northpole.com",
        # Optional, this participant will never be matched to any of the excluded participants
        "exclude": ["Hermie"],
        # Optional, this participant will always be assigned to their rigged match
        "rigged": "Clarice",
    },

    "Clarice": {
        "email": "Clarice@northpole.com",
    },

    "Hermie": {
        "email": "Hermie@northpole.com",
    }
}
