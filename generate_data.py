#!/usr/bin/python

import string
import random
import requests
import json


FEATHERS_URL = 'http://localhost:3030'


def id_generator(size=40, chars=string.ascii_letters + string.digits):
    return '{}{}'.format('0x', ''.join(random.choice(chars) for _ in range(size)))


def post_data(url, data):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    my_response = requests.post(url, data=json.dumps(data), headers=headers)
    if not my_response.ok:
        my_response.raise_for_status()


def get_data(url):
    my_response = requests.get(url)
    if not my_response.ok:
        my_response.raise_for_status()
    return my_response.data


def list_givers(managers):
    return [x for x in managers if x['id'] != 0 and x['contract_details']['paymentState'] == 'Donor']


def list_dacs(managers):
    return [x for x in managers if x['id'] != 0 and x['contract_details']['paymentState'] == 'Delegate']


def list_campaigns(managers):
    return [x for x in managers if x['id'] != 0 and x['contract_details']['paymentState'] == 'Project' and x['contract_details']['parentProject'] == '0']


def list_milestones(managers):
    return [x for x in managers if x['id'] != 0 and x['contract_details']['paymentState'] == 'Project' and x['contract_details']['parentProject'] != '0']


def donate_funds(donation_history, managers, notes, num=1):
    for _ in range(num):
        from_giver = random.choice(list_givers(managers))
        amount = str(random.randint(50, 100))
        donation = {
            'delegates': [],
            'amount': amount,
            'owner': str(from_giver['id']),
            'paymentState': 'NotPaid'
        }
        notes.append({'id': len(notes), 'contract_details': donation})
        donation_history.append({
            'from': from_giver['id'],
            'to': from_giver['id'],
            'amount': amount,
            'type': 'donation'
        })


def delegate_funds(donation_history, managers, notes, num=1):
    for _ in range(num):
        delegate_recipient = random.choice(list_dacs(managers))
        parent_note = random.choice([x for x in notes if x['id'] != 0 and not x['contract_details']['delegates']])
        from_giver = managers[int(parent_note['contract_details']['owner'])]
        amount = str(random.randint(0, int(parent_note['contract_details']['amount'])))
        donation = {
            'delegates': [{
                'id': len(notes),
                'addr': delegate_recipient['contract_details']['addr'],
                'name': delegate_recipient['contract_details']['name']
            }],
            'amount': amount,
            'owner': str(from_giver['id']),
            'paymentState': 'NotPaid'
        }
        parent_note['contract_details']['amount'] = str(int(parent_note['contract_details']['amount']) - int(amount))
        notes.append({'id': len(notes), 'contract_details': donation})
        donation_history.append({
            'from': from_giver['id'],
            'to': delegate_recipient['id'],
            'amount': amount,
            'type': 'delegation'
        })


def transfer_funds(donation_history, managers, notes, num=1):
    for _ in range(num):
        parent_note = random.choice([x for x in notes if x['id'] != 0])
        from_giver = managers[int(parent_note['contract_details']['owner'])]
        recipient = random.choice(list_dacs(managers) + list_campaigns(managers) + list_milestones(managers))
        amount = str(random.randint(0, int(parent_note['contract_details']['amount'])))
        transfer = {
            'delegates': parent_note['contract_details']['delegates'],
            'amount': amount,
            'owner': str(recipient['id']),
            'paymentState': 'NotPaid'
        }
        if parent_note['contract_details']['paymentState'] == 'Project':
            transfer['proposedProject'] = recipient['id']
            transfer['commitTime'] = 1504151606
        parent_note['contract_details']['amount'] = str(int(parent_note['contract_details']['amount']) - int(amount))
        notes.append({'id': len(notes), 'contract_details': transfer})
        donation_history.append({
            'from': from_giver['id'],
            'to': recipient['id'],
            'amount': amount,
            'type': 'delegation'
        })


def make_givers(givers, managers, num=1):
    with open('first_last_names.txt') as f:
        first_last_names = f.readlines()
    for _ in range(num):
        id = len(managers)
        addresss = id_generator()
        name = random.choice(first_last_names).strip()
        giver = {
            'paymentState': 'Donor',
            'addr': addresss,
            'name': name,
            'commitTime': 86400
        }
        managers.append({'id': id, 'contract_details': giver})
        givers.append({
            'id': id,
            'avatar_image': 'blah',
            'addr': addresss,
            'name': name,
        })


def make_dacs(dacs, managers, num=1):
    with open('causes.txt') as f:
        causes = f.readlines()
    with open('animal_pics.txt') as f:
        animal_pics = f.readlines()
    with open('descriptions.txt') as f:
        descriptions = f.readlines()
    for _ in range(num):
        id = len(managers)
        addresss = id_generator()
        name = random.choice(causes).strip()
        dac = {
            'paymentState': 'Delegate',
            'addr': addresss,
            'name': name,
            'commitTime': 86400
        }
        managers.append({'id': id, 'contract_details': dac})
        owner = random.choice(list_givers(managers))
        dacs.append({
            'id': id,
            'image': random.choice(animal_pics).strip(),
            'description': random.choice(descriptions).strip(),
            'owner': owner['id'],
            'addr': addresss,
            'name': name,
        })


def make_campaigns(campaigns, managers, num=1):
    with open('campaign_names.txt') as f:
        campaign_names = f.readlines()
    with open('animal_pics.txt') as f:
        animal_pics = f.readlines()
    with open('descriptions.txt') as f:
        descriptions = f.readlines()
    for _ in range(num):
        id = len(managers)
        addresss = id_generator()
        name = random.choice(campaign_names).strip()
        campaign = {
            'paymentState': 'Project',
            'addr': addresss,
            'name': name,
            'commitTime': 86400,
            'parentProject': '0',
            'canceled': False
        }
        managers.append({'id': id, 'contract_details': campaign})
        owner = random.choice(list_givers(managers))
        campaigns.append({
            'id': id,
            'image': random.choice(animal_pics).strip(),
            'description': random.choice(descriptions).strip(),
            'owner': owner['id'],
            'addr': addresss,
            'name': name,
        })


def make_milestones(milestones, managers, num=1):
    with open('milestone_names.txt') as f:
        milestone_names = f.readlines()
    with open('animal_pics.txt') as f:
        animal_pics = f.readlines()
    with open('descriptions.txt') as f:
        descriptions = f.readlines()
    parent_campaign = random.choice(list_campaigns(managers))
    for _ in range(num):
        id = len(managers)
        addresss = id_generator()
        name = random.choice(milestone_names).strip()
        milestone = {
            'paymentState': 'Project',
            'addr': addresss,
            'name': name,
            'commitTime': 86400,
            'parentProject': parent_campaign['id'],
            'canceled': False
        }
        managers.append({'id': id, 'contract_details': milestone})
        owner = random.choice(list_givers(managers))
        milestones.append({
            'id': id,
            'image': random.choice(animal_pics).strip(),
            'description': random.choice(descriptions).strip(),
            'owner': owner['id'],
            'parent_campaign': parent_campaign['id'],
            'addr': addresss,
            'name': name,
        })


def list_notes(giver_id, notes):
    return [x for x in notes if x['id'] != 0 and x['contract_details']['owner'] == giver_id]


def list_donation_history(id, donation_history):
    return [x for x in donation_history if x['to'] == id or x['from'] == id]


def main():
    # these state objects will be on blockchain and feathers
    managers = [{'id': 0, 'contract_details': None}]
    notes = [{'id': 0, 'contract_details': None}]

    # these state objects will be on feather only
    givers = []
    dacs = []
    campaigns = []
    milestones = []
    donation_history = []

    # generate data with functions that take state objects
    make_givers(givers, managers, 2)
    make_dacs(dacs, managers, 1)
    make_campaigns(campaigns, managers, 1)
    make_milestones(milestones, managers, 2)
    donate_funds(donation_history, managers, notes, 4)
    delegate_funds(donation_history, managers, notes, 4)
    transfer_funds(donation_history, managers, notes, 4)

    # blockchain data grouped by filtered feathers entities
    blockchain = {
        'givers': list_givers(managers),
        'dacs': list_dacs(managers),
        'campaigns': list_campaigns(managers),
        'milestones': list_milestones(managers),
        'notes': notes,
    }

    # feathers data
    feathers = {
        'givers': givers,
        'dacs': dacs,
        'campaigns': campaigns,
        'milestones': milestones,
    }

    # donation data for giver
    donation_data = list_donation_history(givers[0]['id'], donation_history)
    print json.dumps(donation_data, indent=1)

    # post data to feathers server
    # post_data('http://localhost:3030/managers', managers)
    # post_data('http://localhost:3030/notes', notes)
    post_data(FEATHERS_URL + '/givers', givers)
    post_data(FEATHERS_URL + '/causes', dacs)
    post_data(FEATHERS_URL + '/campaigns', campaigns)
    post_data(FEATHERS_URL + '/milestones', milestones)
    # post_data(FEATHERS_URL + '/donations', donation_history)

    # feathers errors preventing generation of new services
    # Couldn't find any versions for "web3-utils" that matches "^1.1.0"
    # error Couldn't find package "web3-requestManager" on the "npm" registry.
    # error Couldn't find package "web3-core-promiEvent" on the "npm" registry.

    # curl command to delete data from service
    # curl 'http://localhost:3030/givers/' -X "DELETE"
    # curl 'http://localhost:3030/causes/' -X "DELETE"
    # curl 'http://localhost:3030/campaigns/' -X "DELETE"
    # curl 'http://localhost:3030/milestones/' -X "DELETE"


if __name__ == '__main__':
    main()
