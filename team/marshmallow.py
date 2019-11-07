from config import ma
from .models import Fantasy_cards
from marshmallow import fields


class CardsSchema(ma.ModelSchema):
    bench_boost = fields.Method('get_bench_boost')
    free_hit = fields.Method('get_free_hit')
    triple_captain = fields.Method('get_triple_captain')
    wild_card = fields.Method('get_wild_card')

    class Meta:
        model = Fantasy_cards

    def get_bench_boost(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.bench_boost]

    def get_free_hit(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.free_hit]

    def get_triple_captain(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.triple_captain]

    def get_wild_card(self, obj):
        card_status = {0: 'inactive', 1: 'active', -1: 'used'}
        return card_status[obj.wild_card]