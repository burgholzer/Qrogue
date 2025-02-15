# Must haves #
- custom GameData location also for Unix!
- automatic font size adaption
  - instead try to start terminal maximized and print clear error message
  - research if it is feasible to make a web app out of Qrogue
- multiple levels

# Should haves #
- PyPI upload:
https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
- implement remaining changes proposed via Feedback
- consider space in backpack when buying from shop
- place collectible on the ground if you cannot pack a reward in your backpack?
- access Backpack (Inventory)

# Tweaks #
- key input pauses?

# Optionals #
- use higher numbers for more difficult Enemies?
- use TextBox instead of BlockLabels?
- add Training-Table to Spaceship (implement with flee rate)


# Ideas #
- ChallengeRooms: only use 3 gates, only 1 Hadamard, only 3 adaptions, ...

# Finished #
- raise Errors in Logger instead of arbitrary positions so we can actually log them!
- implement normal Game Mode (playing without Tutorial Stuff on generated (?) Map)
  - [x] make chance parameter of WildRooms more stable so 0.7 means 70% of 
  all Tiles in the Room are Enemies
  - [x] further enhance Factories for random selection of Collectibles, Riddles, Bosses 
- start in debug mode (HUD logs, all error output, cheats, simulator)
- GameSimulator: seeds need to be set correctly so random stuff like flee chance doesn't hinder execution
- new Hub area
- new Tutorial based on Narrative update
- create Rooms from file
