# Checkers AI Project

This project implements an AI to play Checkers using Backtracking and the Minimax algorithm. The game is developed in Python, utilizing the Pygame library for graphics.

## Getting Started

Follow these steps to set up and run the project:

1. **Prerequisites:**
   - Ensure you have `git` installed and added to your system path.

2. **Setup:**
   - Create a new folder for the project and navigate to it in the terminal.
   - Clone the repository:  
     ```bash
     git clone <repository-url>
     ```
   - Create a virtual Python environment:  
     **Windows:**  
     ```bash
     python -m venv venv
     ```  
     **Mac/Linux:**  
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:  
     **Windows:**  
     ```bash
     ./venv/Scripts/activate
     ```  
     **Mac/Linux:**  
     ```bash
     source venv/bin/activate
     ```
   - Install the required packages:  
     ```bash
     pip install -r requirements.txt
     ```  
     *(Use `pip3` if on Mac/Linux)*

3. **Running the Game:**
   - Start the game by executing:  
     ```bash
     python game.py
     ```  
     *(Use `python3` if on Mac/Linux)*

4. **Troubleshooting:**
   - If you encounter any issues, try deleting the `__pycache__` folder and rerun `game.py`.

## Possible Improvements

1. **Evaluation Function:** Enhance the function used to evaluate board states.
2. **Move Caching:** Implement caching of intermediate moves to reduce recalculations.
3. **Search Depth:** Increase search depth, potentially using `asyncio` to maintain responsiveness.
4. **Openings/Book Moves:** Include standard opening moves and patterns for a more competitive AI.