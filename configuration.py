
# Credentials for the email account used to send santatron emails, gmail is a good choice
ORIGIN_ADDRESS = "santa@gmail.com"
ORIGIN_PASSWORD = "cookies"

# In test mode, all emails will be sent to this address instead of the configured participant addresses (for dry runs)
TEST_EMAIL = "santa@northpole.com"

# Invitation email subject line
INVITATION_SUBJECT = "SECRET SANTA INVITATION :) 01110011010101"

# Invitation email body content, giver and reciever must be provided when email is generated
INVITATION_DATE_STRING = "DECEMBER 25TH, 1 A.D."

INVITATION_TIME_STRING = "12:00 A.M."

INVITATION_ADDRESS = "NORTH POLE"


# Function to generate email body with giver and receiver filled in
def generate_msg(giver, receiver):
    INVITATION_CONTENT = f"""

    THIS MESSAGE IS AUTOMATICALLY GENERATED AND SENT BY SANTATRON 9002. PLEASE DO NOT REPLY :)
    WELCOME TO YOU, HUMAN "{giver}". YOU ARE INVITED TO {INVITATION_ADDRESS} FOR A SECRET SANTA CHRISTMAS PARTY.

    DATE: {INVITATION_DATE_STRING}
    TIME: {INVITATION_TIME_STRING}

    YOU WILL ACT AS "SECRET SANTA" FOR FELLOW HUMAN "{receiver}".

    IF YOU FEEL THE NEED TO TRADE GIFTEES, PLEASE DO SO WITH CAUTION TO ENSURE NO ONE IS LEFT OUT IN THE 'COLD'. (HA! HA!)


    SANTATRON IS ALWAYS WATCHING YOU. ;)


    """
    return INVITATION_CONTENT