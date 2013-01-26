from tournament.competition.models import BracketSlot

for slot in BracketSlot.objects.filter(bracket__category=9).exclude(winner_goes_to=None):
    try:
        slot2 = BracketSlot.objects.exclude(id=slot.id).get(winner_goes_to=slot.winner_goes_to)
        if slot2.no_player:
            slot.status = 2
            slot.save()
            BracketSlot.objects.filter(id=slot.winner_goes_to_id).update(player=slot.player_id)
    except BracketSlot.DoesNotExist:
        pass