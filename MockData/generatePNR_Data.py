""" In accordance with poltiregisterforskriften § 60-5.'Opplysningskategorier som kan registreres' we want to
create mock data based on the data points 1. - 18. that the PNR-register can consist of."""
import string
# Imports
from random import randint, choice, choices
from names import get_last_name, get_first_name
from random_address import real_random_address_by_state
from pandas import read_json, DataFrame
from math import acos, cos, sin, radians
from datetime import timedelta, datetime


class GeneratePNR_number:
    """
        Jf. § 60-5. 1.
        Generates a PNR-number for a record in the PNR-registry of an order.
    """
    def __iter__(self):
        """
            Initializes the PNR-number

            Parameters:
                -

            Returns:
                pnr_number (iterator) : The PNR-number iterator.
        """

        self.pnr_number = 0

        return self

    def __next__(self) -> int:
        """
            Iterates the PNR number

            Parameters:
                -

            Returns:
                pnr_number (int) : The next PNR-number.
        """

        self.pnr_number += 1

        return self.pnr_number


class GenerateTime:
    """
        Jf. § 60-5. 2. & 3. & 13.
        Generates a Date.
    """

    def get_random_datetime(self) -> datetime:
        """
            Picks a random date and time between 1970 and 2030.

            Parameters:
                -

            Returns:
                random_datetime (datetime) : A random time.
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


class GenerateName:
    """
        Jf. § 60-5. 4. & 17.
        Generates a Name.

        Parameters:
            -

        Returns:
            name (str): The name.
    """

    def get_gender(self) -> str:
        """
            Picks a random gender.

            Parameters:
                -

            Returns:
                name (str): The name.
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
                - gender (str) {'male', 'female'} : The gender of the name.

            Returns:
                :raises ValueError, TypeError
                first_name (str) : A first name based on gender.
        """

        gender = self.get_gender()

        first_name = get_first_name(gender)
        return first_name

    def get_last_name(self) -> str:
        """
            Picks a random last name.
            Parameters:
                -

            Returns:
                last_name (str) : A last name.
        """

        last_name = get_last_name()

        return last_name

    def get_middle_name(self) -> str:
        """
            Picks a random middle name of a length.

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

                middle_name += self.get_first_name(gender) + ' '
            else:
                middle_name += self.get_last_name() + ' '

        return middle_name

    def get_full_name(self) -> str:
        """
            Generates a full name. This name consists of a first name + middle name + last name.

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


class GenerateEMail:
    """
        Jf. § 60-5. 5.
        Generates a EMail based on their name.
    """

    def __init__(self):
        self.email_providers = [('gmail', 0.4), ('outlook', 0.15), ('yahoo', 0.05), ('icloud', 0.4)]
        self.email_suffixes = [('com', 0.7), ('no', 0.25), ('org',0.04), ('gov', 0.01)]

    def get_email(self, passenger_full_name: str) -> str:
        """
            Generates a EMail for a record.

            Parameters:
                - passenger_full_name (str) : The full name of the passenger.

            Returns:
                :raises TypeError, ValueError
                email_address (str) : The email address.
        """

        if type(passenger_full_name) != str:
            raise TypeError('Passenger name is not string')
        elif len(passenger_full_name.split(' ')) < 2:
            raise ValueError('Provided incomplete full name')

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


class GeneratePhoneNumber:
    """
        Jf. § 60-5. 5.
        Generates a Phone Number. The number is generated with different prefixes to reflect the diversity
        of the Norwegian demographic, but is restricted to norwegian based numbers e.i. length of 8 and the first digit
        being 4 or 9.

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
                                      ('+94', 0.005), ('+92', 0.005), ('+63', 0.005), ('+7', 0.005), ('+56', 0.0027),
                                      ('+55', 0.0027), ('+502', 0.0027), (f'+{randint(10, 389)}', 0.0096)]
        self.phone_number_starts = [('4', 0.5), ('9', 0.5)]

    def get_phone_number(self) -> str:
        """
            Generates a Phone Number.

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


class GenerateAddress:
    """
        Jf. § 60-5. 5.
        Generates an Address. The address consists of a street name, zip code and city. Pick from a public database
        containing addresses from different states in the United States of America.
    """
    def __init__(self):
        self.states = ['CT', 'MA', 'VT', 'AL', 'AR', 'DC', 'FL', 'GA', 'KY', 'MD', 'OK', 'TN', 'AK', 'AZ', 'CA',
                       'CO']

    def get_address(self) -> tuple:
        """
            Generates an Address.

            Parameters:
                -

            Returns:
                address (tuple(str, int, str)) : The complete address (street name, zip code, city).
        """

        state = self.states[randint(0, len(self.states) - 1)]
        address = real_random_address_by_state(state)

        return address['city'], address['postalCode'], address['address1']


class GeneratePaymentInformation:
    """
        Jf. § 60-5. 6.
        Generates the Payment Information. This information is the vendor and the type of payment.
    """
    def __init__(self):
        self.vendors = ['Mastercard', 'Visa']
        self.payment_types = ['Credit', 'Debit']

    def get_payment_information(self) -> tuple:
        """
            Generates the Payment Information.

            Parameters:
                -

            Returns:
                payment_information (tuple(str,str)) : The payment information with the vendor and type of payment.
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

    def __init__(self):
        self.airport_data = read_json('airport_data.json')
        self.flight_path_lengths = [(2, 0.75), (3, 0.2), (4, 0.045), (5, 0.004), (6, 0.001)]

    def get_random_airport(self):
        """
            Pulls a random airport from the airport_data.json.

            Parameters:
                -

            Returns:
                airport (DataFrame) {iata_code, airport_name, city_name, latitude, longitude} :
                    Information about the airport. IATA code, name, city, latitude, longitude.
        """

        airport = self.airport_data.sample()

        return airport

    def get_travel_plan(self, departure_time) -> list[tuple[str, str, datetime]]:
        """
            Generates a Travel Plan.

            Parameters:
                -

            Returns:
                :raises TypeError
                travel_path (list[tuple(str, str, datetime)]) :
                    The travel destinations and their arrival time, in order, for a given record.
        """

        if type(departure_time) != datetime:
            raise TypeError('Departure time is not datetime')

        path_lengths = [path_length[0] for path_length in self.flight_path_lengths]
        path_length_probabilities = [path_length[1] for path_length in self.flight_path_lengths]
        path_length = choices(path_lengths, path_length_probabilities)[0]

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

    def add_waiting_time_between_fights(self, arrival_time):
        """
            Adds in one hour waiting time between flights

            Parameters:
                - arrival_time (datetime) : The arrival time at the airport from the previous flight.

            Returns:
                :raises TypeError
                departure_time (datetime) : The new departure time of the next flight.
        """

        if type(arrival_time) != datetime:
            raise TypeError('Arrival time is not a datetime')

        departure_time = arrival_time + timedelta(hours=1)

        return departure_time

    def calculate_arrival_time(self, departure_airport, arrival_airport, departure_time) -> int:
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
                arrival_time (datetime) : The time of arrival.
        """

        dataframe_keys = ['iata_code', 'airport_name', 'city_name', 'latitude', 'longitude']

        if type(departure_time) != datetime:
            raise TypeError('Departure time is not datetime')
        elif type(departure_airport) != DataFrame:
            raise TypeError('Departure airport is not DataFrame')
        elif type(arrival_airport) != DataFrame:
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

        arrival_time = departure_time + timedelta(minutes=travel_time_round)

        return arrival_time


class GenerateBonusProgramInformation:
    """
        Jf. § 60-5. 8.
        Generates a Bonus Program information from arbitrary tiers of programs.
    """

    def __init__(self):
        self.programs = [('Gold', 0.5), ('Platinum', 0.35), ('Diamond', 0.15)]

    def get_bonus_program(self) -> str:
        """
            Picks a Bonus Program.

            Parameters:
                -

            Returns:
                program (str) : The name of the bonus program.
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

    def __init__(self):
        self.airlines = [('SAS', ), ('Norwegian', ), ('Widerøe',)]
        self.travel_agencies = [('Balslev', 0.125), ('TUI', 0.125), ('norsktur', 0.125), ('Solfaktor', 0.125),
                                ('Ving', 0.125), ('Chater', 0.125), ('Apollo', 0.125), ('Expedia', 0.125)]

    def get_travel_agency(self) -> str:
        """
            Picks a Travel Agency from a list of norwegian based agencies.

            Parameters:
                -

            Returns:
                agency (str) : The name of the travel agency.
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
                airline (str) : The name of the airline.
        """

        airlines = [airline[0] for airline in self.airlines]
        airlines_probabilities = [airline[1] for airline in self.airlines]
        airline = choices(airlines, airlines_probabilities)[0]

        return airline


class GeneratePassengerStatus:
    """
        Jf. § 60-5. 10.
        Generates the Passenger Status for travels.
    """

    def __init__(self):
        self.passenger_statuses = [('no show', 0.02), ('cancelled', 0.08), ('showed', 0.9)]

    def get_passenger_status(self) -> str:
        """
            Picks the status of a passenger for a departure.

            Parameters:
                -

            Returns:
                status (str) : The status of a passenger for a departure.
        """

        statuses = [status[0] for status in self.passenger_statuses]
        statuses_probabilities = [status[1] for status in self.passenger_statuses]
        status = choices(statuses, statuses_probabilities)[0]

        return status

    def get_full_journey_statuses(self, travel_path: list[str]) -> list[str]:
        """
            Picks the status of all departures for a given travel path.

            Parameters:
                - travel_plan (list[str]) : The travel plan.

            Returns:
                :raises TypeError, ValueError
                departure_statuses (list[str]) : The list of statuses for a travel path.
        """

        if type(travel_path) != list:
            raise TypeError('Travel path is not a list')
        elif len(travel_path) < 1:
            raise ValueError('Travel path is empty')
        elif not all(type(airport) == str for airport in travel_path):
            raise ValueError('Travel path not all strings')

        departure_statuses = []

        for airport in range(len(travel_path)):
            status = self.get_passenger_status()

            if status != 'showed':
                for _ in range(len(travel_path) - len(departure_statuses)):
                    departure_statuses.append('-')

                return departure_statuses
            else:
                departure_statuses.append(status)

        return departure_statuses


class GenerateTicketNumber:
    """
        Jf. § 60-5. 13.
        Generates Ticket Numbers.
    """

    def get_ticket_number(self) -> int:
        """
            Picks a random Ticket NUmber.

            Parameters:
                -

            Returns:
                ticket_number (int) : The Ticket Number.
        """

        ticket_number = randint(100000000, 999999999)

        return ticket_number


class GenerateSeat:
    """
        Jf. § 60-5. 14.
        Generates Seats based on the Boeing 737-800s.
    """

    def __init__(self):
        self.seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']

    def get_seat(self):
        """
            Picks a random Seat.

            Parameters:
                -

            Returns:
                seat (str) : The Seat.
        """

        row = str(randint(1, 32))
        column = choice(self.seat_letters)

        seat = row + column

        return seat

    def get_seats(self, passengers: list[str]) -> list[tuple[str, str]]:
        """
            Picks a Seat to each passenger. Delegation of seats can be in incremental or scattered.

            Parameters:
                - passengers (list[str]) : The list of passengers.

            Returns:
                :raises TypeError, ValueError
                passenger_with_seats (list[tuple[str, str]]) : The list of passengers with their respective seat.
        """

        if type(passengers) != list:
            raise TypeError('Passengers is not a list')
        elif len(passengers) < 1:
            raise ValueError('Passengers empty')
        elif not all(type(passenger) == str for passenger in passengers):
            raise ValueError('Passengers not all strings')

        seat = self.get_seat()
        booked_seats = [seat]

        scattered = randint(0, 1)
        for _ in range(1, len(passengers)):
            if scattered:
                while (seat := self.get_seat()) in booked_seats:
                    continue
            else:
                seat = self.increment_seat(seat)

            booked_seats.append(seat)

        passenger_with_seats = list(zip(passengers, booked_seats))

        return passenger_with_seats

    def increment_seat(self, seat: str) -> str:
        """
            Increments the seat.

            Parameters:
                - seat (str) : The seat to be incremented.

            Returns:
                :raises TypeError, ValueError
                seat (str) : The incremented seat.
        """

        if type(seat) != str:
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


class GenerateLuggage:
    """
    Jf. § 60-5. 16.
    Generates Luggage Information for a given passenger. This information is the amount of cabin luggage with their
    corresponding weights in kilograms, the amount of checked luggage with their corresponding weights in kilograms, and
    the amount of special baggage with their corresponding weights in kilograms.

    """
    def __init__(self):
        self.cabin_luggage_amounts = [('unknown', 1)]
        self.checked_luggage_amounts = [(0, 0.45), (1, 0.3), (2, 0.1), (3, 0.05), (randint(4, 12), 0.1)]
        self.special_baggage_amounts = [(0, 0.9), (1, 0.05), (2, 0.025), (randint(3, 12), 0.025)]

    def get_luggage(self) -> tuple[list, list, list]:
        """
        Jf. § 60-5. 16.
        Generates Luggage Information for a given passenger.

        Parameters:
            -

        Returns:
            cabin_luggage (list) : The weights, in kilograms, of all cabin luggage for the passenger.
            checked_luggage (list) : The weights, in kilograms, of all checked luggage for the passenger.
            special_baggage (list) : The weights, in kilograms, of all special baggage for the passenger.
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


if __name__ == "__main__":
    pass