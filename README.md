# AI_MidTerm

## Requirements
### Setup virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt
```

### Create input files
```bash
cp ./maps/map1.txt ./input.txt # or ./maps/map5.txt
cp ./maps/map1.txt ./adversarial_input.txt # and add 'A' character in a random position for the second agent
```

## Check heuristic command
```bash
python -m Solver.check_heuristic
```

## Run single agent on a map
```bash
python -m GUI.main
```

## Run multi agent
```bash
python -m Adversarial_GUI.adversarial_game
```