""" In accordance with poltiregisterforskriften § 60-5.'Opplysningskategorier som kan registreres' we want to
create mock data based on the data points 1. - 18. that the PNR-register can consist of."""

# Imports
from typing import List

def generatePNR_number() -> int:
    """
    Jf. § 60-5. 1.
    Generates a PNR-number for an entry in the PNR-registry of an order.

    Parameters:
        -

    Returns:
        pnr_number (int) : The PNR-number
    """
    pass


def generateDate() -> int:
    """
    Jf. § 60-5. 2. & 3. & 13.
    Generates a Date.

    Parameters:
        -

    Returns:
        date (int) : The date
    """
    pass


def generateName() -> str:
    """
    Jf. § 60-5. 4. & 17.
    Generates a Name for a passenger.

    Parameters:
        -

    Returns:
        name (str): The name.
    """
    pass


def generateEmail(passenger_name: str) -> str:
    """
    Jf. § 60-5. 5.
    Generates a EMail for a passenger based on their name.

    Parameters:
        -

    Returns:
        email_address (str) : The email address.
    """
    pass


def generatePhoneNumber() -> int:
    """
    Jf. § 60-5. 5.
    Generates a Phone Number.

    Parameters:
        -

    Returns:
        phone_number (int) : The phone number.
    """
    pass


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