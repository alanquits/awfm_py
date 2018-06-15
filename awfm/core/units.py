UNITS = {
    "length": {
        "meters": 1.0,
        "feet": 3.28084
    },
    "time": {
        "days": 1.0,
        "hours": 1/24.0,
        "minutes": 1/(24.0*60.0)
    },
    "discharge": {
        "m3/day": 1.0
    }
}

def unit_conversion_factor(unit_type, unit_from, unit_to):
    # Standard units are meters, days, and m3/day
    to_std = CONVERSION_FACTORS[unit_type][unit_from]
    from_std = 1.0/CONVERSION_FACTORS[unit_type][unit_to]
    return to_std*from_std
