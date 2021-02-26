def calculate_co2(distance_in_km):
    """
    Returns kg for a `distance_in_km`of CO2.

    Source Data is the UK Government Vehicle Licensing Statistics;
    https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2018

    Specifically, we used the breakdown of cars by estimated emissions
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/
    attachment_data/file/800513/veh0206.ods

    And took the Average CO2 (g/km) for all licensed cars at EOY 2018.


    """

    co2_grams_per_km = 141.9
    co2_kg_per_km = co2_grams_per_km / 1000

    return distance_in_km * co2_kg_per_km


def calculate_flight_equivalent(co2):
    """
    Emissions figures for a transatlantic flight from https://www.carbonindependent.org/22.html.

    Flight figures: https://www.flight-durations.com/London-to-New-York
    """
    kg_co2_per_hour = 90
    hr_per_flight = 8  # London to NYC

    co2_per_flight = kg_co2_per_hour * hr_per_flight

    return co2 / co2_per_flight
