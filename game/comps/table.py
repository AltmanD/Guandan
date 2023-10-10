
class Table:
    
    def __init__(self) -> None:
        self.players_on_table_numb = 0
        self.players_on_table_id = []

    def __repr__(self) -> str:
        return 'Table(players_on_table_numb={}, players_on_table_id={})' \
            .format(self.players_on_table_numb, self.players_on_table_id)

    def join(self, player_id_list: list):
        self.players_on_table_numb += len(player_id_list)
        self.players_on_table_id = list(set(self.players_on_table_id + player_id_list))
    
    def detach(self, player_id: int):
        self.players_on_table_numb -= 1
        self.players_on_table_id.remove(player_id)
