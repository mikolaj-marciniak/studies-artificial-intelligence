# Artificial Intelligence Algorithms in Python

This repository contains academic projects developed as part of an Artificial Intelligence and Knowledge Engineering course. The project focuses on implementing selected AI algorithms in Python, including graph search, route planning, optimization, and heuristic game-playing agents.

The repository is divided into two main parts:

- `Lista1` – graph search and route optimization using public transport data
- `Lista2` – heuristic AI agent for the Breakthrough board game

## Project Overview

The main goal of this repository is to practice implementing AI algorithms from scratch and applying them to practical problems. The first part focuses on route planning using GTFS public transport data, while the second part focuses on decision-making in a two-player board game.

## Part 1 – Route Planning and Optimization

The first part of the project implements algorithms for finding routes in a public transport network. The application works with GTFS data and builds a graph representation of connections between stops.

Implemented algorithms include:

- Dijkstra’s algorithm
- A* search
- heuristic A* variants
- Tabu Search for optimization

The route planning module supports searching for routes based on different criteria, such as travel time or number of transfers.

## Part 2 – Breakthrough Game Agent

The second part of the project implements an AI player for the board game Breakthrough. The application models the game board, players, moves, and game state, and uses search-based decision-making to choose moves.

Implemented concepts include:

- game state representation
- legal move generation
- Minimax algorithm
- alpha-beta pruning
- heuristic board evaluation
- automated AI vs AI gameplay simulation

The project includes several heuristic components used to evaluate board positions, such as material balance, pawn advancement, pawn structure, and the position of the furthest pawn.

## Technologies

- Python
- Object-Oriented Programming
- Graph Algorithms
- Dijkstra’s Algorithm
- A* Search
- Tabu Search
- Minimax
- Alpha-Beta Pruning
- Heuristics
- GTFS Data Processing

## Repository Structure

```text
studies-artificial-intelligence/  
├── Lista1/  
│   └── src/  
│       ├── a_star.py  
│       ├── a_star_heuristic.py  
│       ├── dijkstra.py  
│       ├── graph.py  
│       ├── gtfs_data.py  
│       ├── tabu_search.py  
│       └── ...  
│  
├── Lista2/  
│   └── src/  
│       ├── board.py  
│       ├── game.py  
│       ├── move.py  
│       ├── player.py  
│       ├── minimax.py  
│       ├── heuristics.py  
│       └── ...  
│  
└── README.md
```

## Author

Mikołaj Marciniak
