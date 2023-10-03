""" In accordance with poltiregisterforskriften § 60-5.'Opplysningskategorier som kan registreres' we want to
create mock data based on the data points 1. - 18. that the PNR-register can consist of."""

# Imports
from random import randint, choices
from typing import List
import names

class GeneratePNR_number():
    """
    Jf. § 60-5. 1.
    Generates a PNR-number for an entry in the PNR-registry of an order.
    """
    def __iter__(self):
        """
            Parameters:
                -

            Returns:
                pnr_number (iterator) : The PNR-number iterator.
        """

        self.pnr_number = 0
        return self

    def __next__(self) -> int:
        """
            Parameters:
                -

            Returns:
                pnr_number (int) : The next PNR-number.
        """

        self.pnr_number += 1
        return self.pnr_number


def generateDate() -> int:
    """
    Jf. § 60-5. 2. & 3. & 13.
    Generates a Date.

    Parameters:
        -

    Returns:
        date (int) : The date.
    """
    pass


class GenerateName():
    """
    Jf. § 60-5. 4. & 17.
    Generates a Name for a passenger.

    Parameters:
        -

    Returns:
        name (str): The name.
    """

    def __init__(self):
        self.names = names

    def get_gender(self) -> str:
        gender = 'female'

        gender_male = randint(0, 1)
        if gender_male:
            gender = 'male'

        return gender

    def get_first_name(self, gender) -> str:
        """
        Parameters:
            - gender (str) {'male', 'female'} : The gender of the name.

        Returns:
            first_name (str) : A first name based on gender.
        """

        first_name = self.names.get_first_name(gender)
        return first_name

    def get_last_name(self) -> str:
        """
        Parameters:
            -

        Returns:
            last_name (str) : A last name.
        """

        last_name = self.names.get_last_name()

        return last_name

    def get_middle_name(self) -> str:
        """
        Parameters:
            -

        Returns:
            middle_name (str) : A middle name.
        """

        middle_name_amount_distribution = [(0, 0.5), (1, 0.34), (2, 0.14), (3, 0.01), (randint(4, 12), 0.01)]
        middle_names_amounts = [names_amount[0] for names_amount in middle_name_amount_distribution]
        middle_names_amount_probabilities = [names_amount[1] for names_amount in middle_name_amount_distribution]
        middle_names_amount = choices(middle_names_amounts, middle_names_amount_probabilities)[0]

        middle_name = ''
        for _ in range(middle_names_amount):

            type_first_name = randint(0, 1)

            if type_first_name:
                gender = self.get_gender()

                middle_name += self.names.get_first_name(gender) + ' '
            else:
                middle_name += self.names.get_last_name() + ' '

        return middle_name

    def get_full_name(self) -> str:
        """
        Parameters:
            - gender (str) {'male', 'female'} : The gender of the full name

        Returns:
            full_name (str) : A full name based on gender.
        """

        gender = self.get_gender()
        first_name = self.names.get_first_name(gender)
        middle_name = self.get_middle_name()
        last_name = self.get_last_name()

        full_name = f'{first_name} {middle_name}{last_name}'

        return full_name

class GenerateEMail():
    """
    Jf. § 60-5. 5.
    Generates a EMail for a passenger based on their name.
    """

    def __init__(self):
        self.email_providers = [('gmail', 0.4), ('outlook', 0.15), ('yahoo', 0.05), ('icloud', 0.4)]
        self.email_suffixes = [('com', 0.7), ('no', 0.25), ('org',0.04), ('gov', 0.01)]

    def get_email(self, passenger_full_name: str) -> str:
        """
        Parameters:
            - passenger_full_name (str) : The full name of the passenger.

        Returns:
            email_address (str) : The email address.
        """

        providers = [provider[0] for provider in self.email_providers]
        providers_probability = [provider[1] for provider in self.email_providers]
        provider = choices(providers, providers_probability)[0]

        suffixes = [suffix[0] for suffix in self.email_suffixes]
        suffixes_probabilities = [suffix[1] for suffix in self.email_suffixes]
        suffix = choices(suffixes, suffixes_probabilities)[0]

        full_name = passenger_full_name.split(' ')
        stem = ''
        for i in range(len(full_name)):
            stem += full_name[i].lower()

            if i != len(full_name):
                stem += '.'


        email_address = f'{stem}@{provider}.{suffix}'
        return email_address

class GeneratePhoneNumber():
    """
    Jf. § 60-5. 5.
    Generates a Phone Number.

    Parameters:
        -

    Returns:
        phone_number (int) : The phone number.
    """

    def __init__(self):
        self.phone_number_prefixes = [('+47', 0.82), ('+46', 0.0065), ('+45', 0.00032), ('+354', 0.00001),
                                      ('+358', 0.00032), ('+48', 0.0016), ('+387', 0.0016), ('+44', 0.0016),
                                      ('+34', 0.0016), ('+49', 0.0016), ('+380', 0.0016), ('+372', 0.0016),
                                      ('+30', 0.0016), ('+355', 0.0023), ('+252', 0.015), ('+254', 0.015),
                                      ('+234', 0.015), ('+220', 0.015), ('+27', 0.015), ('+20', 0.015), ('+98', 0.005),
                                      ('+964', 0.005), ('+93', 0.005), ('+66', 0.005), ('+84', 0.005), ('+86', 0.005),
                                      ('+94', 0.005), ('+91', 0.005), ('+63', 0.005), ('+7', 0.005), ('+56', 0.0027),
                                      ('+55', 0.0027), ('+502', 0.0027), (f'+{randint(10, 389)}', 0.0096)]
        self.phone_number_starts = [('4', 0.5), ('9', 0.5)]

    def get_phone_number(self) -> str:
        """
        Parameters:
            -

        Returns:
            phone_number (int) : The phone number.
        """

        phone_number_length = 8

        prefixes = [prefix[0] for prefix in self.phone_number_prefixes]
        prefixes_probabilities = [prefix[1] for prefix in self.phone_number_prefixes]
        prefix = choices(prefixes, prefixes_probabilities)[0]

        number_starts = [number_start[0] for number_start in self.phone_number_starts]
        number_starts_probabilities = [number_start[1] for number_start in self.phone_number_starts]
        number_start = choices(number_starts, number_starts_probabilities)[0]

        remaining_digits = ''.join(map(str, (randint(0, 9) for _ in range(phone_number_length - len(number_start)))))

        return f'{prefix} {number_start}{remaining_digits}'


def generateAddress() -> tuple(str, int, str):
    """
    Jf. § 60-5. 5.
    Generates an Address.

    Parameters:
        -

    Returns:
        address (tuple(str, int, str)) : The complete address (street name, zip code, city).
    """
    pass


def generatePaymentInformation() -> tuple(str, str):
    """
    Jf. § 60-5. 6.
    Generates the Payment Information for an order. This information is the vendor and the type of payment.

    Parameters:
        -

    Returns:
        payment_information (tuple(str,str)) : The payment information with the vendor and type of payment.
    """
    pass


def generateTravelPlan() -> List[tuple(str, int)]:
    """
    Jf. § 60-5. 7.
    Generates a Travel Plan for a passenger. This plan is the travel path, in order, with the corresponding arrival time.
    Except for the first entry as it is the departure location and therefore the associated time is the time of departure.

    Parameters:
        -

    Returns:
        travel_path (List[str]) : The travel destinations and their arrival time, in order, for a given passenger.
    """
    pass


def generateBonusProgram() -> str:
    """
    Jf. § 60-5. 8.
    Generates a Bonus Program used for a given order.

    Parameters:
        -

    Returns:
        bonus_program (str) : The name of the bonus program.
    """
    pass


def generateTravelAgency() -> str:
    """
    Jf. § 60-5. 9.
    Generates a Travel Agency for a given order.

    Parameters:
        -

    Returns:
        travel_agency (str) : The name of the travel agency.
    """
    pass


def generatePassengerStatus() -> str:
    """
    Jf. § 60-5. 10.
    Generates the Passenger Status.

    Parameters:
        -

    Returns:
        passenger_status (str) : The status of a passenger
    """
    pass


def generateTicketNumber() -> int:
    """
    Jf. § 60-5. 13.
    Generates a Ticket Number for a ticket.

    Parameters:
        -

    Returns:
        ticket_number (int) : The ticket number.
    """
    pass


def generateSeatNumber() -> str:
    """
    Jf. § 60-5. 14.
    Generates a Seat Numbers for a passenger.


    Parameters:
        -

    Returns:
        passenger_seats (str) : The seat for a passenger.
    """
    pass


def generateLuggage() -> List[int]:
    """
    Jf. § 60-5. 16.
    Generates Luggage Information for a given passenger. This information is the amount of cabin luggage with their
    corresponding weight. And the amount of checked luggage with their corresponding weight.

    Parameters:
        -

    Returns:
        cabin_luggage (List[int]) : The weights of all cabin luggage for the passenger.
        checked_luggage (List[int]) : The weights of all checked luggage for the passenger.
    """
    pass

if __name__ == "__main__":
    pass