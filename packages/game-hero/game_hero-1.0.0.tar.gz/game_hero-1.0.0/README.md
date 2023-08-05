# Game Hero
The project developed covers a story game based on turn based combat, where the game hero encounters a wild beast in the forest. Game character's stats are taken into consideration on each turn, whilst the game herop also possesses some additional skills to help him in battle.

### The story 
Once upon a time there was a great hero, called Orderus, with some strengths and weaknesses, as all heroes have. 
After battling all kinds of monsters for more than a hundred years, Orderus now has the following stats: 
- Health: 70 - 100 
- Strength: 70 - 80 
- Defence: 45 – 55 
- Speed: 40 – 50 
- Luck: 10% - 30% (0% means no luck, 100% lucky all the time). 

Also, he possesses 2 skills: 

- Rapid strike: Strike twice while it’s his turn to attack; there’s a 10% chance he’ll use this skill every time he attacks 
- Magic shield: Takes only half of the usual damage when an enemy attacks; there’s a 20% change he’ll use this skill every time he defends. 
 
### Gameplay 
As Orderus walks the ever-green forests of the Game, he encounters some wild beasts, with the 
following properties: 
- Health: 60 - 90 
- Strength: 60 - 90 
- Defence: 40 – 60 
- Speed: 40 – 60 
- Luck: 25% - 40% 

The game simulates a battle between Orderus and a wild beast. On every battle, Orderus and the beast are initialized with random properties, within their ranges. 

The first attack is done by the player with the higher speed. If both players have the same speed, than the attack is carried on by the player with the highest luck. 
After an attack, the players switch roles: the attacker now defends and the defender now attacks. 

The damage done by the attacker is calculated with the following formula: 
~ **Damage = Attacker strength – Defender defence**

The damage is subtracted from the defender’s health. An attacker can miss their hit and do no  damage if the defender gets lucky that turn.  Orderus’ skills occur randomly, based on their chance on each turn. 
### Game over 
The game ends when one of the players remain without health or the number of turns reaches 20. 
The application outputs the results for each turn: what happened, which skills were used (if any), the damage done, defender’s health left. 
Additionally, a winner may be declared if we have a winner before the maximum number of rounds is reached. 
