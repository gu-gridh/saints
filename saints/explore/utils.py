from collections import defaultdict

from django.db.models import Q

from .models import Iconographic


def build_iconographic_lookup(cults):
    iconographics = [
        icon
        for cult in cults
        for icon in cult.relation_iconographic.all()
    ]

    keys = {
        (icon.card, icon.volume)
        for icon in iconographics
    }

    if not keys:
        return {}

    query = Q()

    for card, volume in keys:
        query |= Q(card=card, volume=volume)

    additional_map = defaultdict(list)

    for item in Iconographic.objects.filter(query).values(
        'id',
        'card',
        'volume',
        'motif2',
        'filename',
        'uri',
    ):
        additional_map[
            (item['card'], item['volume'])
        ].append({
            'id': item['id'],
            'motif2': item['motif2'],
            'filename': item['filename'],
            'uri': item['uri'],
        })

    return additional_map