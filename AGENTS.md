# Swarmancer - Agent Instructions (AGENTS.md)

This document provides architectural context and development guidelines for any AI agents or developers working on **Swarmancer**, an official submission for the file named "The Long PyGame Summer Jam".

## 1. Architectural Paradigm: Hybrid ECS & OOP

This project operates on a hybrid Entity-Component-System (ECS) architecture while maintaining Object-Oriented Programming (OOP) encapsulation for specific game entities.

- **The ECS Core:** Logic is separated from data to maintain high performance. Logic (Systems) acts on purely flat data (Components).
- **OOP Containers:** Your OOP classes act as specialized prefabs or containers that automatically equip the necessary components upon initialization.

## 2. SOLID Principles & Modularity

All code must adhere to SOLID principles to ensure a clean, maintainable structure.

- **Single Responsibility:** Components hold only data, Systems contain only processing logic, and Entities act only as initialization bundles.
- **Proactive File Generation:** Do not be hesitant to generate new files in applying the SOLID principles to make the code more modular and cleaner. If a file, system, or component grows too complex, actively split it into new, focused modules to maintain strict architectural boundaries.

## 3. Spec-Driven Development (SDD)

To aggressively combat scope creep, this project strictly adheres to Spec-driven development.

- **The `/docs` Directory:** All project blueprints and design documentation reside in the `/docs` directory.
- **Hierarchy:** Work is organized into Epics, Features, and User Stories.
- **Agent Rule:** Before implementing any new feature, refer to the User Stories for the exact acceptance criteria. If a mechanic is not documented, do not build it.

## 4. Directory Structure Rules

When generating or modifying code, strict adherence to the project directory structure is required:

- `components/`: The pure data layer holding attributes like velocity, coordinates, and health values.
- `entities/`: Houses your OOP containers that bundle components together.
- `systems/`: The logic layer that processes entities based on their components.
- `utils/`: Helper modules for math or optimization, specifically storing the SpatialHash grid logic.
- `docs/`: Holds the design documentation for Spec-driven development.

## 5. Coding Standards & Performance

- **Global Imports Only:** Do not add import statements inside functions or methods. Doing so in a game loop severely impacts the performance of the game. All imports must be placed at the top of the file.
