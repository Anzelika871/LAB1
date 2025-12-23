from __future__ import annotations
import random
from random import getrandbits
from typing import List, Optional
from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class MyBot(Player):
    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
            self, playable_cards: List[Card], top_card: Card, current_color: CardColor
    ) -> None:
        self._top_card = top_card
        self._current_color = current_color

    def choose_action(self) -> PlayerAction:

        possible = [c for c in self.hand
                    if c.can_play_on(self._top_card, self._current_color)]

        if not possible:
            return PlayerAction(draw_card=True)

        color_score = {}
        for card in self.hand:
            if card.color not in color_score:
                color_score[card.color] = 0
            color_score[card.color] += 1

        preferred_color = max(color_score, key=color_score.get, default=None)

        card_to_play = None

        special_types = ['DRAW_TWO', 'REVERSE', 'SKIP']
        for special in special_types:
            for card in possible:
                if hasattr(card.label, special) and getattr(card.label, special):
                    card_to_play = card
                    break
            if card_to_play:
                break

        if not card_to_play:
            number_cards = [c for c in possible if 0 <= c.label <= 9]
            if number_cards:
                # Предпочитаем карты нужного цвета
                colored = [c for c in number_cards if c.color == preferred_color]
                card_to_play = colored[0] if colored else number_cards[0]

        if not card_to_play and len(self.hand) < 3:
            wild_cards = [c for c in possible if hasattr(c.label, 'WILD')]
            if wild_cards:
                card_to_play = wild_cards[0]

        if not card_to_play:
            card_to_play = possible[0]

        return PlayerAction(card=card_to_play, draw_card=False)

    def choose_color(self, wild_card: Card) -> CardColor:
        color_weights = {}
        for card in self.hand:
            if hasattr(card, 'color') and card.color:
                color_weights[card.color] = color_weights.get(card.color, 0) + 1

        if color_weights:
            return max(color_weights, key=color_weights.get)

        from random import choice
        return choice([CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW])

    def decide_say_uno(self) -> bool:
        return len(self.hand) == 1

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        return drawn_card.can_play_on(self._top_card, self._current_color)