from datetime import timedelta
import random


def generate_random_date(start_date, end_date, output_format):
    delta = end_date - start_date
    random_date = start_date + timedelta(days=random.randint(0, delta.days))
    return random_date.strftime(output_format)
