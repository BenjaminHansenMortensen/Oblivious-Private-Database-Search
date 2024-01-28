""" In accordance with poltiregisterforskriften § 60-5.'Opplysningskategorier som kan registreres' we want to
create mock data based on the data points 1. - 18. that the PNR-register can consist of. """

# Imports
from random import randint, choice, choices
from names import get_last_name, get_first_name
from random_address import real_random_address_by_state
from pandas import read_json, DataFrame
from math import acos, cos, sin, radians
from datetime import timedelta, datetime
from json import dump

# Local getters imports.
from Oblivious_Private_Database_Search.getters import (get_records_directory as
                                                       records_directory)
from Oblivious_Private_Database_Search.getters import (get_supplementary_data_directory as
                                                       supplementary_data_directory)


class GenerateNumber:
    """
        Jf. § 60-5. 1.
        Generates a PNR-number for a record in the PNR-registry of an order.
    """
    def __iter__(self, init_number: int = -1):
        """
            Initializes the PNR-number

            Parameters:
                -

            Returns:
                - pnr_number (iterator) : The PNR-number iterator.
        """

        self.pnr_number = init_number

        return self

    def __next__(self) -> int:
        """
            Iterates the PNR number

            Parameters:
                -

            Returns:
                - pnr_number (int) : The next PNR-number.
        """

        self.pnr_number += 1

        return self.pnr_number


class GenerateDateAndTime:
    """
        Jf. § 60-5. 2. & 3. & 13.
        Generates a Date and Time.
    """

    @staticmethod
    def get_random_datetime() -> datetime:
        """
            Picks a random date and time between 1970 and 2030.

            Parameters:
                -

            Returns:
                - random_datetime (datetime) : A random date and time.
        """

        start_date = datetime(1970, 1, 1)
        end_date = datetime(2030, 12, 31)
        days = (end_date - start_date).days
        random_day = randint(1, days)
        random_hour = randint(1, 23)
        random_minute = randint(0, 5) * 10 + randint(0, 1) * 5

        random_date = start_date + timedelta(days=random_day)
        random_datetime = random_date.replace(hour=random_hour, minute=random_minute)

        return random_datetime

    @staticmethod
    def get_departure_datetime(order_datetime: datetime) -> datetime:
        """
            Picks the date and time of the departure depending on the order time.

            Parameters:
                -

            Returns:
                - departure_datetime (datetime) : The time of departure.
        """

        random_day = randint(1, 60)
        random_hour = randint(1, 23)
        random_minute = randint(0, 5) * 10 + randint(0, 1) * 5

        departure_date = order_datetime + timedelta(days=random_day)
        departure_datetime = departure_date.replace(hour=random_hour, minute=random_minute)

        return departure_datetime


class GenerateName:
    """
        Jf. § 60-5. 4. & 17.
        Generates a Name.

        Parameters:
            -

        Returns:
            - name (str): The name.
    """

    @staticmethod
    def get_gender() -> str:
        """
            Picks a random gender.

            Parameters:
                -

            Returns:
                - name (str): The name.
        """

        gender = 'female'

        gender_male = randint(0, 1)
        if gender_male:
            gender = 'male'

        return gender

    def get_first_name(self) -> str:
        """
            Picks a random first name.

            Parameters:
                -

            Returns:
                :raises
                - first_name (str) : A first name.
        """

        gender = self.get_gender()

        first_name = get_first_name(gender)
        return first_name

    @staticmethod
    def get_last_name() -> str:
        """
            Picks a random last name.
            Parameters:
                -

            Returns:
                - last_name (str) : A last name.
        """

        last_name = get_last_name()

        return last_name

    def get_middle_name(self) -> str:
        """
            Picks a random middle name of a length.

            Parameters:
                -

            Returns:
                - middle_name (str) : A middle name.
        """

        middle_name_amount_distribution = [(0, 0.5), (1, 0.34), (2, 0.14), (3, 0.01), (randint(4, 12), 0.01)]
        middle_names_amounts = [names_amount[0] for names_amount in middle_name_amount_distribution]
        middle_names_amount_probabilities = [names_amount[1] for names_amount in middle_name_amount_distribution]
        middle_names_amount = choices(middle_names_amounts, middle_names_amount_probabilities)[0]

        middle_name = ''
        for _ in range(middle_names_amount):

            type_first_name = randint(0, 1)

            if type_first_name:
                middle_name += self.get_first_name() + ' '
            else:
                middle_name += self.get_last_name() + ' '

        return middle_name

    def get_full_name(self) -> str:
        """
            Generates a full name. This name consists of a first name + middle name + last name.

            Parameters:
                -

            Returns:
                - full_name (str) : A full name.
        """

        first_name = self.get_first_name()
        middle_name = self.get_middle_name()
        last_name = self.get_last_name()

        full_name = f'{first_name} {middle_name}{last_name}'

        return full_name

    def get_full_names(self, amount: int) -> list[str]:
        """
            Generates a list of full name. These names consist of a first name + middle name + last name.

            Parameters:
                -

            Returns:
                - full_names (list[str]) : A list of full names based.
        """

        names = [self.get_full_name() for _ in range(amount)]

        return names


class GenerateEmail:
    """
        Jf. § 60-5. 5.
        Generates an Email based on their name.
    """

    def __init__(self) -> None:
        self.email_providers = [('gmail', 0.4), ('outlook', 0.15), ('yahoo', 0.05), ('icloud', 0.4)]
        self.email_suffixes = [('com', 0.7), ('no', 0.25), ('org', 0.04), ('gov', 0.01)]

        return

    def get_email(self, full_name: str) -> str:
        """
            Generates an Email for a record.

            Parameters:
                - passenger_full_name (str) : The full name of the passenger.

            Returns:
                :raises TypeError, ValueError
                - email_address (str) : The email address.
        """

        if type(full_name) is not str:
            raise TypeError('Passenger name is not string')
        elif len(full_name.split(' ')) < 2:
            raise ValueError('Provided incomplete full name')

        providers = [provider[0] for provider in self.email_providers]
        providers_probability = [provider[1] for provider in self.email_providers]
        provider = choices(providers, providers_probability)[0]

        suffixes = [suffix[0] for suffix in self.email_suffixes]
        suffixes_probabilities = [suffix[1] for suffix in self.email_suffixes]
        suffix = choices(suffixes, suffixes_probabilities)[0]

        full_name = full_name.split(' ')
        stem = ''
        for i in range(len(full_name)):
            stem += full_name[i].lower()

            if i != len(full_name):
                stem += '.'

        email_address = f'{stem}@{provider}.{suffix}'
        return email_address


class GeneratePhoneNumber:
    """
        Jf. § 60-5. 5.
        Generates a Phone Number. The number is generated with different prefixes to reflect the diversity
        of the Norwegian demographic, but is restricted to norwegian based numbers e.i. length of 8 and the first digit
        being 4 or 9.

        Parameters:
            -

        Returns:
            - phone_number (int) : The phone number.
    """

    def __init__(self) -> None:
        self.phone_number_prefixes = [('+47', 0.82), ('+46', 0.0065), ('+45', 0.00032), ('+354', 0.00001),
                                      ('+358', 0.00032), ('+48', 0.0016), ('+387', 0.0016), ('+44', 0.0016),
                                      ('+34', 0.0016), ('+49', 0.0016), ('+380', 0.0016), ('+372', 0.0016),
                                      ('+30', 0.0016), ('+355', 0.0023), ('+252', 0.015), ('+254', 0.015),
                                      ('+234', 0.015), ('+220', 0.015), ('+27', 0.015), ('+20', 0.015), ('+98', 0.005),
                                      ('+964', 0.005), ('+93', 0.005), ('+66', 0.005), ('+84', 0.005), ('+86', 0.005),
                                      ('+94', 0.005), ('+92', 0.005), ('+63', 0.005), ('+7', 0.005), ('+56', 0.0027),
                                      ('+55', 0.0027), ('+502', 0.0027), (f'+{randint(10, 389)}', 0.0096)]
        self.phone_number_starts = [('4', 0.5), ('9', 0.5)]

        return

    def get_phone_number(self) -> str:
        """
            Generates a Phone Number.

            Parameters:
                -

            Returns:
                - phone_number (int) : The phone number.
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


class GenerateAddress:
    """
        Jf. § 60-5. 5.
        Generates an Address. The address consists of a street name, zip code and city. Pick from a public database
        containing addresses from different states in the United States of America.
    """
    def __init__(self) -> None:
        self.states = ['CT', 'MA', 'VT', 'AL', 'AR', 'DC', 'FL', 'GA', 'KY', 'MD', 'OK', 'TN', 'AK', 'AZ', 'CA', 'CO']

        return

    def get_address(self) -> tuple:
        """
            Generates an Address.

            Parameters:
                -

            Returns:
                - address (tuple(str, int, str)) : The complete address (street name, zip code, city).
        """

        state = self.states[randint(0, len(self.states) - 1)]
        address = real_random_address_by_state(state)

        try:
            return address['city'], address['postalCode'], address['address1']
        except KeyError:
            return '*unknown*', address['postalCode'], address['address1']


class GeneratePaymentInformation:
    """
        Jf. § 60-5. 6.
        Generates the Payment Information. This information is the vendor and the type of payment.
    """
    def __init__(self) -> None:
        self.vendors = ['Mastercard', 'Visa']
        self.payment_types = ['Credit', 'Debit']

        return

    def get_payment_information(self) -> tuple:
        """
            Generates the Payment Information.

            Parameters:
                -

            Returns:
                - payment_information (tuple(str,str)) : The payment information with the vendor and type of payment.
        """

        vendor = self.vendors[randint(0, len(self.vendors) - 1)]
        payment_type = self.payment_types[randint(0, len(self.payment_types) - 1)]

        return vendor, payment_type


class GenerateTravelPlan:
    """
        Jf. § 60-5. 7.
        Generates a Travel Plan. This plan is the travel path with the corresponding arrival time.
        Except for the first entry as it is the departure location and therefor the associated time is the time of
        departure.
    """

    def __init__(self) -> None:
        self.airport_data = read_json(supplementary_data_directory() / "airport_data.json")
        self.flight_path_lengths = [(2, 0.75), (3, 0.2), (4, 0.045), (5, 0.004), (6, 0.001)]

        return

    def get_path_length(self) -> int:
        """
            Picks a length for the travel path.

            Parameters:
                -

            Returns:
                - path_length (int) : The length of the travel path.
        """

        path_lengths = [path_length[0] for path_length in self.flight_path_lengths]
        path_length_probabilities = [path_length[1] for path_length in self.flight_path_lengths]
        path_length = choices(path_lengths, path_length_probabilities)[0]

        return path_length

    def get_random_airport(self) -> DataFrame:
        """
            Pulls a random airport from the airport_data.json.

            Parameters:
                -

            Returns:
                - airport (DataFrame) {iata_code, airport_name, city_name, latitude, longitude} :
                    Information about the airport. IATA code, name, city, latitude, longitude.
        """

        airport = self.airport_data.sample()

        return airport

    def get_travel_plan(self, departure_time, path_length: int) -> list[tuple]:
        """
            Generates a Travel Plan.

            Parameters:
                - departure_time (datetime) : The time of departure.

            Returns:
                :raises TypeError
                - travel_plan (list[tuple(str, str, str, datetime)]) :
                    The travel plan consisting of airport code, airport name, city name and time.
        """

        if type(departure_time) is not datetime:
            raise TypeError('Departure time is not datetime')

        travel_path = [self.get_random_airport() for _ in range(path_length)]

        travel_plan = []

        departure_airport = travel_path[0]
        airport_code = departure_airport['iata_code'].values[0]
        airport_name = departure_airport['airport_name'].values[0]
        airport_city = departure_airport['city_name'].values[0]
        travel_plan.append((airport_code, airport_name, airport_city, departure_time))

        for airport in travel_path[1:]:
            airport_code = airport['iata_code'].values[0]
            airport_name = airport['airport_name'].values[0]
            airport_city = airport['city_name'].values[0]
            arrival_time = self.calculate_arrival_time(departure_airport, airport, departure_time)
            travel_plan.append((airport_code, airport_name, airport_city, arrival_time))

            departure_airport = airport
            departure_time = self.add_waiting_time_between_fights(arrival_time)

        return travel_plan

    @staticmethod
    def add_waiting_time_between_fights(arrival_datetime) -> datetime:
        """
            Adds in one hour waiting time between flights

            Parameters:
                - arrival_time (datetime) : The arrival time at the airport from the previous flight.

            Returns:
                :raises TypeError
                - departure_time (datetime) : The new departure time of the next flight.
        """

        if type(arrival_datetime) is not datetime:
            raise TypeError('Arrival time is not a datetime')

        departure_time = arrival_datetime + timedelta(hours=1)

        return departure_time

    @staticmethod
    def calculate_arrival_time(departure_airport, arrival_airport, departure_datetime) -> int:
        """
            Finds the distance between to airports and calculates the arrival time based on the departure time and how
            long the flight would take.

            Parameters:
                - departure_airport (DataFrame) {iata_code, airport_name, city_name, latitude, longitude} :
                    The airport to be departed.
                - arrival_airport (DataFrame) {iata_code, airport_name, city_name, latitude, longitude} :
                    The arrival airport.
                - departure_time (datetime) : The time of departure.

            Returns:
                :raises TypeError, KeyError
                - arrival_time (datetime) : The time of arrival.
        """

        dataframe_keys = ['iata_code', 'airport_name', 'city_name', 'latitude', 'longitude']

        if type(departure_datetime) is not datetime:
            raise TypeError('Departure time is not datetime')
        elif type(departure_airport) is not DataFrame:
            raise TypeError('Departure airport is not DataFrame')
        elif type(arrival_airport) is not DataFrame:
            raise TypeError('Departure airport is not DataFrame')
        elif not all(key in dataframe_keys for key in departure_airport.keys().values):
            raise KeyError('Departure airport have incorrect keys')
        elif not all(key in dataframe_keys for key in arrival_airport.keys().values):
            raise KeyError('Arrival airport have incorrect keys')

        airplane_speed = 12   # 12 Kilometers per Minute
        additional_time = 15  # Additional time due to reduced speed on take off and landing
        real_path_deviation = 1.3   # Time lost with the real flight path

        departure_latitude = radians(departure_airport['latitude'].values[0])
        departure_longitude = radians(departure_airport['longitude'].values[0])
        arrival_latitude = radians(arrival_airport['latitude'].values[0])
        arrival_longitude = radians(arrival_airport['longitude'].values[0])

        distance = int(acos(sin(departure_latitude) * sin(arrival_latitude) +
                            cos(departure_latitude) * cos(arrival_latitude) *
                            cos(arrival_longitude - departure_longitude)) * 6371)

        time = distance / airplane_speed  # Minutes
        travel_time = int((time + additional_time) * real_path_deviation)
        travel_time_round = round(travel_time / 5) * 5

        arrival_time = departure_datetime + timedelta(minutes=travel_time_round)

        return arrival_time


class GenerateBonusProgramInformation:
    """
        Jf. § 60-5. 8.
        Generates a Bonus Program information from arbitrary tiers of programs.
    """

    def __init__(self) -> None:
        self.programs = [('None', 0.6), ('Gold', 0.25), ('Platinum', 0.10), ('Diamond', 0.05)]

        return

    def get_bonus_program(self) -> str:
        """
            Picks a Bonus Program.

            Parameters:
                -

            Returns:
                - program (str) : The name of the bonus program.
        """

        programs = [program[0] for program in self.programs]
        programs_probabilities = [program[1] for program in self.programs]
        program = choices(programs, programs_probabilities)[0]

        return program


class GenerateTravelInformation:
    """
    Jf. § 60-5. 9.
    Generates the Travel information, that is the travel agency and airline.
    """

    def __init__(self) -> None:
        self.airlines = [('SAS', 0.4), ('Norwegian', 0.4), ('Wideroe', 0.2)]
        self.travel_agencies = [('Balslev', 0.125), ('TUI', 0.125), ('Norsktur', 0.125), ('Solfaktor', 0.125),
                                ('Ving', 0.125), ('Charter', 0.125), ('Apollo', 0.125), ('Expedia', 0.125)]

        return

    def get_travel_agency(self) -> str:
        """
            Picks a Travel Agency from a list of norwegian based agencies.

            Parameters:
                -

            Returns:
                - agency (str) : The name of the travel agency.
        """

        agencies = [agency[0] for agency in self.travel_agencies]
        agencies_probabilities = [agency[1] for agency in self.travel_agencies]
        agency = choices(agencies, agencies_probabilities)[0]

        return agency

    def get_airline(self) -> str:
        """
            Picks an Airline from a list of norwegian based airlines.

            Parameters:
                -

            Returns:
                - airline (str) : The name of the airline.
        """

        airlines = [airline[0] for airline in self.airlines]
        airlines_probabilities = [airline[1] for airline in self.airlines]
        airline = choices(airlines, airlines_probabilities)[0]

        return airline


class GenerateStatusInformation:
    """
        Jf. § 60-5. 10.
        Generates the Passenger Status for travels.
    """

    def __init__(self) -> None:
        self.passenger_statuses = [('no show', 0.02), ('cancelled', 0.08), ('showed', 0.9)]

        return

    def get_passenger_status(self) -> str:
        """
            Picks the status of a passenger for a departure.

            Parameters:
                -

            Returns:
                - status (str) : The status of a passenger for a departure.
        """

        statuses = [status[0] for status in self.passenger_statuses]
        statuses_probabilities = [status[1] for status in self.passenger_statuses]
        status = choices(statuses, statuses_probabilities)[0]

        return status

    def get_passenger_statuses(self, travel_length: int) -> list[str]:
        """
            Picks the status of all departures for a given travel.

            Parameters:
                - travel_length (int) : The travel length.

            Returns:
                :raises TypeError, ValueError
                - departure_statuses (list[str]) : The list of statuses for all destinations.
        """

        if type(travel_length) is not int:
            raise TypeError('Travel length is not a list')
        elif travel_length < 1:
            raise ValueError('Travel length is too short')

        departure_statuses = []

        for airport in range(travel_length):
            status = self.get_passenger_status()

            departure_statuses.append(status)

            if status != 'showed':
                for _ in range(travel_length - len(departure_statuses)):
                    departure_statuses.append('-')

                return departure_statuses

        return departure_statuses

    def get_passengers_statuses(self, passenger_amount: int, travel_length: int) -> list[list[str]]:
        """
            Picks the status of all departures for a given travel path.

            Parameters:
                - travel_plan (int) : The travel length.
                - passenger_amount (int) : The amount of passengers.

            Returns:
                :raises TypeError, ValueError
                - departure_statuses (list[list[str]]) : The list of statuses for all passengers for all destination.
        """

        if type(travel_length) is not int:
            raise TypeError('Travel length is not a list')
        elif travel_length < 1:
            raise ValueError('Travel length is too short')
        elif type(passenger_amount) is not int:
            raise TypeError('Passenger amount is not a list')
        elif passenger_amount < 1:
            raise ValueError('Passenger amount is too small')

        passenger_statuses = [self.get_passenger_statuses(travel_length) for _ in range(passenger_amount)]

        return passenger_statuses


class GenerateTicketNumber:
    """
        Jf. § 60-5. 13.
        Generates Ticket Numbers.
    """

    @staticmethod
    def get_ticket_number() -> int:
        """
            Picks a random Ticket NUmber.

            Parameters:
                -

            Returns:
                - ticket_number (int) : The Ticket Number.
        """

        ticket_number = randint(100000000, 999999999)

        return ticket_number


class GenerateSeatInformation:
    """
        Jf. § 60-5. 14.
        Generates Seats based on the Boeing 737-800s.
    """

    def __init__(self) -> None:
        self.seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']

        return

    def get_seat(self) -> str:
        """
            Picks a random Seat.

            Parameters:
                -

            Returns:
                - seat (str) : The Seat.
        """

        row = str(randint(1, 32))
        column = choice(self.seat_letters)

        seat = row + column

        return seat

    def get_seats(self, passengers_amount: int) -> list[str]:
        """
            Picks a Seat to each passenger. Delegation of seats can be in incremental or scattered.

            Parameters:
                - passengers_amount (int) : The amount of passengers.

            Returns:
                :raises TypeError, ValueError
                - booked_seats (list[str]) : The list of seats for the passengers.
        """

        if type(passengers_amount) is not int:
            raise TypeError('Passengers is not an integer')
        elif passengers_amount < 1:
            raise ValueError('No passengers')

        seat = self.get_seat()
        booked_seats = [seat]

        scattered = randint(0, 1)
        for _ in range(1, passengers_amount):
            if scattered:
                while (seat := self.get_seat()) in booked_seats:
                    continue
            else:
                seat = self.increment_seat(seat)

            booked_seats.append(seat)

        return booked_seats

    def get_travel_seats(self, travel_length: int, passengers_amount: int) -> list[list[str]]:
        """
            Picks a Seat to each passenger for each flight. Delegation of seats can be in incremental or scattered.

            Parameters:
                - travel_length (int) : The length of the travel.
                - passengers_amount (int) : The amount of passengers.

            Returns:
                :raises TypeError, ValueError
                - booked_seats (list[list[str]]) : The list of seats for the passengers for each flight.
        """

        if type(passengers_amount) is not int:
            raise TypeError('Passengers is not an integer')
        elif type(travel_length) is not int:
            raise TypeError('Travel length is not an integer')
        elif passengers_amount < 1:
            raise ValueError('No passengers')
        elif travel_length < 1:
            raise ValueError('No travel')

        booked_seats = [[] for _ in range(passengers_amount)]

        for _ in range(travel_length):
            flight_seats = self.get_seats(passengers_amount)
            for i in range(passengers_amount):
                booked_seats[i].append(flight_seats[i])

        return booked_seats

    def increment_seat(self, seat: str) -> str:
        """
            Increments the seat.

            Parameters:
                - seat (str) : The seat to be incremented.

            Returns:
                :raises TypeError, ValueError
                - seat (str) : The incremented seat.
        """

        if type(seat) is not str:
            raise TypeError('Seat is not a string.')
        try:
            row = int(seat[:-1])
            column = seat[-1]

            if column not in self.seat_letters:
                raise ValueError('Seat is not on the correct format.')
            elif row not in range(1, 33):
                raise ValueError('Seat is not on the correct format.')
        except Exception:
            raise ValueError('Seat is not on the correct format.')

        row = int(seat[:-1])
        column_number = self.seat_letters.index(seat[-1])

        if column_number == len(self.seat_letters) - 1:
            row = (row + 1) % 33

            if row == 0:
                row = 1

        column_number = (column_number + 1) % len(self.seat_letters)

        seat = str(row) + self.seat_letters[column_number]

        return seat


class GenerateLuggageInformation:
    """
        Jf. § 60-5. 16.
        Generates Luggage Information for a given passenger. This information is the amount of cabin luggage with their
        corresponding weights in kilograms, the amount of checked luggage with their corresponding weights in kilograms,
        and the amount of special baggage with their corresponding weights in kilograms.
    """
    def __init__(self):
        self.cabin_luggage_amounts = [('*unknown*', 1)]
        self.checked_luggage_amounts = [(0, 0.45), (1, 0.3), (2, 0.1), (3, 0.05), (randint(4, 12), 0.1)]
        self.special_baggage_amounts = [(0, 0.9), (1, 0.05), (2, 0.025), (randint(3, 12), 0.025)]

    def get_luggage(self) -> tuple[list, list, list]:
        """
            Jf. § 60-5. 16.
            Generates Luggage Information for a given passenger.

            Parameters:
                -

            Returns:
                - cabin_luggage (list) : The weights, in kilograms, of all cabin luggage for the passenger.
                - checked_luggage (list) : The weights, in kilograms, of all checked luggage for the passenger.
                - special_baggage (list) : The weights, in kilograms, of all special baggage for the passenger.
        """

        cabin_luggage_amounts = [luggage[0] for luggage in self.cabin_luggage_amounts]
        cabin_luggage_amounts_probabilities = [luggage[1] for luggage in self.cabin_luggage_amounts]
        cabin_luggage = choices(cabin_luggage_amounts, cabin_luggage_amounts_probabilities)[0]

        cabin_luggage = [cabin_luggage]

        checked_luggage_amounts = [luggage[0] for luggage in self.checked_luggage_amounts]
        checked_luggage_amounts_probabilities = [luggage[1] for luggage in self.checked_luggage_amounts]
        checked_luggage_amount = choices(checked_luggage_amounts, checked_luggage_amounts_probabilities)[0]

        checked_luggage = [(randint(90, 230) / 10) for _ in range(checked_luggage_amount)]

        special_baggage_amounts = [luggage[0] for luggage in self.special_baggage_amounts]
        special_baggage_amounts_probabilities = [luggage[1] for luggage in self.special_baggage_amounts]
        special_baggage_amount = choices(special_baggage_amounts, special_baggage_amounts_probabilities)[0]

        special_baggage = [(randint(90, 320) / 10) for _ in range(special_baggage_amount)]

        return cabin_luggage, checked_luggage, special_baggage

    def get_passengers_luggage(self, passenger_amount: int) -> list[tuple[list, list, list]]:
        """
        Jf. § 60-5. 16.
        Generates Luggage Information for a given passenger.

        Parameters:
            -

        Returns:
            - passengers_luggage (list[tuple[list, list, list]]) :
                The weights, in kilograms, of all luggage for the passengers.
        """

        passengers_luggage = []

        for _ in range(passenger_amount):
            passengers_luggage.append(self.get_luggage())

        return passengers_luggage


class GeneratePassengerInformation:

    def __init__(self) -> None:
        self.amounts = [(1, 0.4), (2, 0.2), (3, 0.2), (4, 0.1), (randint(5, 10), 0.1)]

        return

    def get_amount_of_passengers(self) -> int:
        """
            Generates an amount of passengers for a record.

            Parameters:
                -

            Returns:
                - amount (int) : An amount.
        """

        amounts = [amount[0] for amount in self.amounts]
        amounts_probabilities = [amount[1] for amount in self.amounts]
        amount = choices(amounts, amounts_probabilities)[0]

        return amount


def create_random_record(pnr_number: int) -> dict:
    """
        Generates a PNR record. This record contains the travel information of one order, which is the following
        information:
            - PNR Number
            - Payment Information
                - Ticket Number
                - Date
                - Name
                - Address
                    - City
                    - Zip Code
                    - Street
                - Phone Number
                - Email
                - Vendor
                - Type
                - Bonus Program
            - Airline
            - Travel Agency
            - Travel Plan
                - IATA Code
                - Airport Name
                - City
                - Time
            - Passengers
                - Name
                - Statuses
                - Seat
                - Luggage
                    - Cabin
                    - Checked
                    - Special

        All information is generated in a structured form to create a somewhat realistic record.

        Parameters:
            - pnr_number (int) : The PNR number.

        Returns:
            pnr_record (dict) : A record of one order.
    """

    gen_payment_information = GeneratePaymentInformation()
    gen_ticket_number = GenerateTicketNumber()
    gen_datetime = GenerateDateAndTime()
    gen_name = GenerateName()
    gen_address = GenerateAddress()
    gen_phone_number = GeneratePhoneNumber()
    gen_email = GenerateEmail()
    gen_bonus_program_information = GenerateBonusProgramInformation()
    gen_travel_information = GenerateTravelInformation()
    gen_travel_plan = GenerateTravelPlan()
    gen_status = GenerateStatusInformation()
    gen_seat = GenerateSeatInformation()
    gen_luggage = GenerateLuggageInformation()
    gen_passenger_information = GeneratePassengerInformation()

    ticket_number = gen_ticket_number.get_ticket_number()
    order_datetime = gen_datetime.get_random_datetime()
    orderer_name = gen_name.get_full_name()
    orderer_address = gen_address.get_address()
    orderer_phone_number = gen_phone_number.get_phone_number()
    orderer_email = gen_email.get_email(orderer_name)
    payment_vendor, payment_type = gen_payment_information.get_payment_information()
    order_bonus_program = gen_bonus_program_information.get_bonus_program()
    airline = gen_travel_information.get_airline()
    travel_agency = gen_travel_information.get_travel_agency()
    travel_length = gen_travel_plan.get_path_length()
    departure_time = gen_datetime.get_departure_datetime(order_datetime)
    travel_plan = gen_travel_plan.get_travel_plan(departure_time, travel_length)

    passenger_amount = gen_passenger_information.get_amount_of_passengers()
    passenger_names = gen_name.get_full_names(passenger_amount - 1)
    passenger_names.append(orderer_name)
    passenger_statuses = gen_status.get_passengers_statuses(passenger_amount, travel_length)
    passenger_seats = gen_seat.get_seats(passenger_amount)
    passenger_luggage = gen_luggage.get_passengers_luggage(passenger_amount)

    pnr_record = {'PNR Number': pnr_number,
                  'Payment Information': {'Ticket Number': ticket_number,
                                          'Date': order_datetime.strftime("%d/%m/%Y"),
                                          'Name': orderer_name,
                                          'Address': {'City': orderer_address[0],
                                                      'Zip Code': orderer_address[1],
                                                      'Street': orderer_address[2]
                                                      },
                                          'Phone Number': orderer_phone_number,
                                          'Email': orderer_email,
                                          'Vendor': payment_vendor,
                                          'Type': payment_type,
                                          'Bonus Program': order_bonus_program
                                          },
                  'Airline': airline,
                  'Travel Agency': travel_agency,
                  'Travel Plan': {f"Destination {i + 1}": {'IATA Code': travel_plan[i][0],
                                                           'Airport Name': travel_plan[i][1],
                                                           'City': travel_plan[i][2],
                                                           'Time': travel_plan[i][3].strftime("%d/%m/%Y, %H:%M:%S"),
                                                           } for i in range(travel_length)

                                  },
                  'Passengers': {f'Passenger {passenger + 1}': {'Name': passenger_names[passenger],
                                                                'Status': {f'Destination {i + 1}':
                                                                           passenger_statuses[passenger][i]
                                                                           for i in range(travel_length)
                                                                           },
                                                                'Seat': passenger_seats[passenger],
                                                                'Luggage': {'Cabin': passenger_luggage[passenger][0],
                                                                            'Checked': passenger_luggage[passenger][1],
                                                                            'Special': passenger_luggage[passenger][2]
                                                                            }
                                                                } for passenger in range(passenger_amount)
                                 }
                  }

    return pnr_record


def run(size: int) -> None:
    number_of_records = size

    gen_pnr_number = iter(GenerateNumber())

    for _ in range(number_of_records):
        pnr_number = next(gen_pnr_number)
        pnr_record = create_random_record(pnr_number)
        pnr_record_path = records_directory() / f'record{pnr_number}.json'

        with pnr_record_path.open('w') as f:
            dump(pnr_record, f, indent=4)
            f.close()

    return
