from werkzeug.exceptions import BadRequest


def validate_cards_active(cards, selected_card):
    if (selected_card == 'Bench Boost' and cards.bench_boost == 0) and (cards.free_hit == 0 or cards.free_hit == -1) \
            and (cards.triple_captain == 0 or cards.triple_captain == -1) \
            and (cards.wild_card == 0 or cards.wild_card == -1):
        return 1

    elif (selected_card == 'Free Hit' and cards.free_hit == 0) and (cards.bench_boost == 0 or cards.bench_boost == -1) \
            and (cards.triple_captain == 0 or cards.triple_captain == -1) \
            and (cards.wild_card == 0 or cards.wild_card == -1):
        return 2

    elif (selected_card == 'Triple Captain' and cards.triple_captain == 0) and (
            cards.bench_boost == 0 or cards.bench_boost == -1) \
            and (cards.free_hit == 0 or cards.free_hit == -1) \
            and (cards.wild_card == 0 or cards.wild_card == -1):
        return 3

    elif (selected_card == 'Wild Card' and cards.wild_card == 0) and (cards.bench_boost == 0 or cards.bench_boost == -1) \
            and (cards.free_hit == 0 or cards.free_hit == -1) \
            and (cards.triple_captain == 0 or cards.triple_captain == -1):
        return 4
    else:
        raise BadRequest(description="failed to activating")


def validate_cards_cancel(cards, selected_card):
    if selected_card == 'Bench Boost' and cards.bench_boost == 1:
        return 1

    elif selected_card == 'Free Hit' and cards.free_hit == 1:
        return 2

    elif selected_card == 'Triple Captain' and cards.triple_captain == 1:
        return 3

    elif selected_card == 'Wild Card' and cards.wild_card == 1:

        return 4
    else:
        raise BadRequest(description="failed to canceling")