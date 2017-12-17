import random
import datetime
from collections import Counter

__author__ = "William Hardy Gest"
__version__ = "1.0"

try:
    import yagmail
except ModuleNotFoundError as e:
    print("External library 'yagmail' required to send emails. Try 'pip install -r requirements.txt'")
    exit()

try:
    from participants import PARTICIPANTS
except ModuleNotFoundError as e:
    print("No 'participants.py' file found.")
    exit()

try:
    import configuration
except ModuleNotFoundError as e:
    print("No 'configuration.py' file found.")
    exit()

# Change to False to send emails to participant accounts and seal their fates
TEST_MODE = True


class ParticipantsFileError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class InvalidResultsError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


def assign_participants():
    completed_assignments = {}
    invalid_matches_for_participant = {}
    available_recievers = list(PARTICIPANTS.keys())
    available_givers = list(PARTICIPANTS.keys())

    # Randomize order
    participants_list = list(PARTICIPANTS.items())
    participants_list.sort(key=lambda x: random.randint(1, 256))

    # Assign any rigged selections
    for name, data in participants_list:
        rigged_match = data.get('rigged')
        if rigged_match:
            completed_assignments[name] = rigged_match
            available_givers.remove(name)
            available_recievers.remove(rigged_match)

    # Randomly assign remaining participants
    for name, data in [p for p in participants_list if p[0] in available_givers]:
        exclude = data.get('exclude', [])

        # Add excluded participants and self to list of invalid options
        invalid_recipients = list(exclude)
        invalid_recipients.append(name)

        # Add reciprocal match, if applicable, to list of invalid options
        try:
            who_has_me_already = [k for k, v in completed_assignments.items() if v == name].pop()
            invalid_recipients.append(who_has_me_already)
        except IndexError:
            who_has_me_already = None

        # Store copy of invalid matches for later use if needed
        invalid_matches_for_participant[name] = list(invalid_recipients)

        # Remove invalid options from final selection
        available_recievers_for_giver = set(available_recievers).difference(invalid_recipients)

        # Match and remove receiver from pool
        try:
            match = random.choice(list(available_recievers_for_giver))
            if match == who_has_me_already:
                raise InvalidResultsError
            completed_assignments[name] = match
            available_recievers.remove(match)

        except IndexError:
            # No valid match available for the last participant, trading matches
            invalid_recipient_to_trade = available_recievers[0]

            # Find a valid trade partner with this epic listcomp
            try:
                trade_partner = random.choice([p[0] for p in participants_list
                                               if completed_assignments.get(p[0])
                                               and invalid_recipient_to_trade not in invalid_matches_for_participant.get(p[0], [])
                                               and completed_assignments.get(p[0], None) not in invalid_recipients])
                match = invalid_recipient_to_trade
                available_recievers.remove(match)
            except (IndexError, KeyError):
                raise ParticipantsFileError("The restrictions in your participant file cannot be satisfied."
                                            " No possible solution.")

            # Do the trade
            completed_assignments[name] = completed_assignments[trade_partner]
            completed_assignments[trade_partner] = match

        invalid_matches_for_participant.get(match, []).append(name)

    test_results(completed_assignments)
    print("Assignments successful under configured restrictions.")
    return completed_assignments


def test_results(completed_assignments):
    # Insurance policy. These tests will always run before email sending, but should never fail without
    # code changes or impossible or malformed participants input data
    for name, data in PARTICIPANTS.items():
        if name not in completed_assignments.keys():
            print("Invalid results:", name, "not matched")
            print(completed_assignments)
            raise InvalidResultsError

        if name not in completed_assignments.values():
            print("Invalid results:", name, "not receiving")
            print(completed_assignments)
            raise InvalidResultsError

        if completed_assignments[completed_assignments[name]] == name:
            print("Invalid results: Reciprocal match:", name, "and", completed_assignments[name])
            print(completed_assignments)
            raise InvalidResultsError

        if completed_assignments[name] in data['exclude']:
            print("Invalid results:", name, "assigned to excluded participant", completed_assignments[name])
            print(completed_assignments)
            raise InvalidResultsError

        if data.get('rigged') and completed_assignments[name] != data.get('rigged'):
            print("Invalid results: Rigged match for", name, "and", data.get('rigged'), "not respected.")
            print(completed_assignments)
            raise InvalidResultsError


def send_emails(completed_assignments):

    yag = yagmail.SMTP(configuration.ORIGIN_ADDRESS, configuration.ORIGIN_PASSWORD)

    for participant in completed_assignments:
        if TEST_MODE:
            email_address = configuration.TEST_EMAIL
        else:
            email_address = PARTICIPANTS[participant]["email"]

        msg = configuration.generate_msg(participant, completed_assignments[participant])
        try:
            yag.send(email_address, subject=configuration.INVITATION_SUBJECT, contents=msg)
            print(f"Successfully sent email to {participant} ({email_address})")
        except:
             print(f"Mail to {email_address} failed!")

    return True


def validate_participants_file():
    if len(PARTICIPANTS) < 3:
        raise ParticipantsFileError(f"Not enough participants for meaningful matching. ({len(PARTICIPANTS)} found.")

    all_names = [n for n, d in PARTICIPANTS.items()]

    for name, data in PARTICIPANTS.items():
        exclude = data.get('exclude', [])
        rigged = data.get('rigged', None)

        if not data.get('email'):
            raise ParticipantsFileError(f"Participant '{name}' has no configured email address.")

        if rigged and rigged not in all_names:
            raise ParticipantsFileError(f"Rigged match '{rigged}' is not a participant.")

        if rigged and rigged == name:
            raise ParticipantsFileError(f"{name} is rigged to themself.")

        invalid_excludes = [x for x in exclude if x not in all_names]
        if exclude and len(invalid_excludes):
            raise ParticipantsFileError(f"'{invalid_excludes[0]}' is not a participant but is present in exclude list for '{name}'")

        if rigged and rigged in exclude:
            raise ParticipantsFileError(f"Participant '{name}' is rigged for '{rigged}', who is excluded.")

    all_rigged = [data.get('rigged') for name, data in PARTICIPANTS.items() if data.get('rigged')]
    duplicates = [key for key, count in Counter(all_rigged).items() if count > 1]

    if len(duplicates):
        raise ParticipantsFileError(f"More than one person is rigged for participant '{duplicates[0]}'.")


def main():
    validate_participants_file()

    print(f"Santatron is attempting to assign {len(PARTICIPANTS)} participants...")

    completed_assignments = assign_participants()
    now = datetime.datetime.now().strftime('%m-%d-%y')
    with open(f"santatron_assignments_{now}.txt", "w") as assignments_record:
        assignments_record.write(str(completed_assignments))

    send_emails(completed_assignments)

    print("Santratron operation complete!")

if __name__ == "__main__":
    main()
