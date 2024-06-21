import time
import random
import logging
from datetime import datetime

import requests

from config import VOTERS_TURNOUT


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = 'http://localhost:5000/register'


MIN_VOTING_AGE = 18
PRACTICAL_MAX_VOTING_AGE = 70


def get_registration_age(dor, dob):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return (datetime.strptime(dor, date_format) - datetime.strptime(dob, date_format)).days // 365


def set_voter_counts_per_state(ratio):
    voter_counts = {}
    for state, (vep, _, _) in VOTERS_TURNOUT.items():
        voter_counts[state] = int(vep * ratio)
    return voter_counts


def fetch_voter_data(num_voters):
    url = f'https://randomuser.me/api/?results={num_voters}&nat=us'
    response = requests.get(url, timeout=20)
    data = response.json()
    voters = data['results']
    voter_list = []
    for voter in voters:
        registration_age = get_registration_age(voter['registered']['date'], voter['dob']['date'])
        if registration_age < MIN_VOTING_AGE or voter['dob']['age'] > PRACTICAL_MAX_VOTING_AGE:
            continue
        voter_info = {
            'full_name': f"{voter['name']['first']} {voter['name']['last']}",
            'registered': voter['registered']['date'],
            'dob': voter['dob']['date'],
            'gender': voter['gender'][0]
        }
        voter_list.append(voter_info)
    return voter_list


def produce_registration_events():
    voter_counts = set_voter_counts_per_state(1 / 10000)
    try:
        while voter_counts:
            for voter in fetch_voter_data(500):
                if not voter_counts:
                    break
                state = random.choice(list(voter_counts))
                voter['state'] = state
                voter_counts[state] -= 1
                if not voter_counts[state]:
                    voter_counts.pop(state)

                event = {
                    'event_type': 'registration',
                    'voter': voter
                }
                requests.post(API_URL, json=event)
                logger.info("Produced registration event: %s", event)
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    produce_registration_events()
