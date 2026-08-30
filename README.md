# Swarmancer

**Swarmancer** is a fast-paced dark fantasy survival arena game built in Pygame. This project is an official submission for "The Long PyGame Summer Jam" hosted on Itch.io.

## Overview

In Swarmancer, you act as the central commander of a fluid horde of tiny skeleton minions. Rather than controlling a single avatar, your active minion count serves directly as your health bar. You must guide your undead army across a dark fantasy battlefield, steering them toward open glowing graves to replenish your ranks and offset constant combat attrition.

Surviving requires seamless navigation and tactical movement to evade escalating enemy threats, including charging peasant militia, explosive dwarf sappers, and stationary stone wizard towers firing wide beams of holy light. The game relies on a custom Entity-Component-System (ECS) architecture to efficiently process the underlying swarm intelligence and fluid mechanics.

## Setup & Installation

This project uses `pipenv` for dependency management to ensure a clean, isolated environment.

### Prerequisites

- Python 3.10+
- [Pipenv](https://pipenv.pypa.io/en/latest/) installed (`pip install pipenv`)

### Installation Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/DragunWF/Swarmancer
   cd Swarmancer
   ```

2. **Install dependencies:**
   This will create a virtual environment and install Pygame (or pygame-ce) as specified in the Pipfile.

```bash
pipenv install
```

3. Run the game:
   Launch the game loop through the Pipenv shell.

```bash
pipenv run python main.py
```
