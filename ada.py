import pandas as pd
import numpy as np
import random

class Player():
    """Represents a player"""
    
    def __init__(self, name):
        """Initialise player object."""
        self.name = name # this attibute holds the name of the player
        self.characters = [] # this attribute holds the characters in the player's deck
        self.status = 1 # this is an attribute to keep track of whether a player is using the last character in their deck
        
    def draw(self, no, data):
        """Draws a random character and adds it to the player's list of characters"""
            # no: how many characters should be drawn?
            # data: a Pandas dataframe with columns 'character' and 'probability'
        for x in range(0, no):
            r = random.random()
            data['cumprob'] = np.cumsum(data['probability'])
            char = data.loc[data.cumprob > r].nsmallest(1,'cumprob')
            self.characters.append(char.iloc[0]['character'])
            
    def add_characters(self, char):
        """Add characters to the player's character deck."""
        for c in char:
            self.characters.append(c)
            
    def battle_random(self, battle, stake):
        """Draws characters for battle and for stakes."""
            # battle: how many characters should each player select for battle?
            # stake: how many characters should each player select for stakes?
            
        if len(self.characters) >= battle + stake:
            """If the player has enough characters, just draw characters as specified."""
            self.battle = random.sample(self.characters,battle)
            for x in self.battle:
                self.characters.remove(x)
            self.stake = random.sample(self.characters,stake)
            for x in self.stake:
                self.characters.remove(x)
            print(self.name + " battle characters: " + str(self.battle))
            print(self.name + " characters at stake: " + str(self.stake))
        
        elif len(self.characters) >= battle + 1:
            """If the player has enough characters for battle but not for stake, draw battle characters as defined and use the remaining characters as stake."""
            self.battle = random.sample(self.characters,battle)
            for x in self.battle:
                self.characters.remove(x)
            self.stake = random.sample(self.characters,len(self.characters))
            for x in self.stake:
                self.characters.remove(x)
            print(self.name + " battle characters: " + str(self.battle))
            print(self.name + " characters at stake: " + str(self.stake))
        
        elif len(self.characters) > 1:
            """If the player does not have enough characters for battle but has more than 1 character, we will draw 1 stake character and use the remaining characters for battle."""
            self.stake = random.sample(self.characters,1)
            for x in self.stake:
                self.characters.remove(x)
            self.battle = random.sample(self.characters,len(self.characters))
            for x in self.battle:
                self.characters.remove(x)
            print(self.name + " battle characters: " + str(self.battle))
            print(self.name + " characters at stake: " + str(self.stake))
        
        elif len(self.characters) == 1:
            """Otherwise, the player's final character will be both stake and battle."""
            self.stake = random.sample(self.characters,1)
            self.battle = random.sample(self.characters,1)
            self.characters = []
            self.status = 0
            print(self.name + " battle characters: " + str(self.battle))
            print(self.name + " characters at stake: " + str(self.stake))
        
        else:
            """Error handling."""
            print('Something went wrong!')
    
    def set_status(self, val):
        """Set the status of the player."""
        if val == 1 or val == 0:
            self.status = val
        else:
            print('Value for status should be either 0 or 1!') 
            
def battle_gameround(players, battle, stake, data):
    """Plays one gameround of a match between the given players"""
        # players: a list of Player() objects
        # battle: how many characters should each player select for battle?
        # stake: how many characters should each player select for stakes?
        # data: a Pandas dataframe with columns 'character' and 'strength'
        
    stakes = []
    winners = []
    win = 0
    for p in players:

        """We generate battle and stake characters for the player."""
        p.battle_random(battle,stake)

        """We compute total battle strength for the player, and compare to the battle strength of other players."""
        s = 0
        for c in p.battle:
            s += data[data['character'] == c].iloc[0]['strength']
        if s > win:
            winners = [p]
            win = s
        elif s == win:
            winners.append(p)
            win = s
        for c in p.stake:
            stakes.append(c)

    if len(winners) == 1:
        """If we have one winner, we add the combined stakes to their character deck, and we give each player back their battle characters."""
        print('The winner of the gameround is ' + winners[0].name + ' with a battle strength of ' + str(win) + '!')
        for p in players:
            if p == winners[0] and p.status == 1:
                print(p.name + ' receives the combined stakes: ' + str(stakes))
                p.add_characters(stakes)
                p.add_characters(p.battle)
            elif p == winners[0] and p.status == 0:
                print(p.name + ' receives the combined stakes: ' + str(stakes))
                p.set_status(1)
                p.add_characters(stakes)
            elif p.status == 1:
                p.add_characters(p.battle)
            else:
                print(p.name + ' has lost all of their characters!')

    else:
        """If we have a tie between multiple players, all players get back their battle and stake characters, and all winners get to draw 1 additional character."""
        t = 'We have a tie! The winners are '
        for w in winners:
            t = t + w.name + ' '
            w.draw(1,data)
            if w.status == 0:
                w.set_status(1)
        t = t + 'with a strength of ' + str(win) + '.'
        print(t)
        for p in players:
            if p.status == 0:
                p.add_characters(p.battle)
            else:
                p.add_characters(p.stake)
                p.add_characters(p.battle)
    
def battle_match(num_players, num_chars, battle, stake, data):
    """Plays all gamerounds of a match between a given number of players."""
        # num_players: how many players are in the match?
        # num_chars: how many characters do the players draw at the start of the match?
        # battle: how many characters should each player select for battle?
        # stake: how many characters should each player select for stakes?
        # data: a Pandas dataframe with columns 'character', 'probability', and 'strength'
        
    """First we check if all the inputs all have appropriate values."""
    if isinstance(num_players,int) and isinstance(num_chars,int) and isinstance(battle,int) and isinstance(stake,int) and isinstance(data,pd.DataFrame) and 'character' in data.columns and 'probability' in data.columns and 'strength' in data.columns and data[['probability']].sum()[0] == 1 and num_players >= 2: 
        
        """Initialise players"""
        players = []
        for n in range(0,num_players):
            p = Player('Player ' + str(n+1))
            p.draw(num_chars, data)
            print(p.name + ' added ' + str(num_chars) + ' characters to their deck!')
            print(p.name + ' deck: ' + str(p.characters))
            players.append(p)

        gameround = 0 # gameround counter
        stat = 1 # should we continue playing another gameround?

        """Start playing!"""
        while stat == 1:
            gameround += 1
            print('Gameround ' + str(gameround))
            battle_gameround(players, battle, stake, data)
            for p in players:
                if p.status == 0:
                    players.remove(p)
            if gameround >= 100:
                """Always include a proper stopping condition in your while loop!"""
                stat = 0
                print('We give up after 100 gamerounds. The player with the highest combined strength in their character deck wins.')
                win = 0
                winners = []
                for p in players:
                    s = 0
                    for c in p.characters:
                        s += data[data['character'] == c].iloc[0]['strength']
                    if s > win:
                        winners = [p]
                        win = s
                    elif s == win:
                        winners.append(p)
                        win = s
                if len(winners) == 1:
                    print('The winner of the game is ' + winners[0].name + ' with a battle strength of ' + str(win) + '!')
                else:
                    t = 'We have a tie! The winners are '
                    for w in winners:
                        t = t + w.name + ' '
                        w.draw(1)
                        if w.status == 0:
                            w.set_status(1)
                    t = t + 'with a strength of ' + str(win) + '.'
                    print(t)
            if len(players) == 1:
                """If there is only one player left, they will be the winner of the match."""
                stat = 0
                print('We have a winner after ' + str(gameround) + ' gamerounds!')
                print('The winner is ' + players[0].name + '.')
    
    elif 'character' not in data.columns or 'probability' not in data.columns or 'strength' not in data.columns:
        print('Make sure your dataframe contains the columns character, probability, and strength!')
    elif data[['probability']].sum()[0] != 1:
        print('Make sure the probabilities of all your characters sum to 1!')
    elif num_players < 2:
        print('Make sure you have at least two players!')
    else:
        print('Make sure all your inputs have appropriate values!')
