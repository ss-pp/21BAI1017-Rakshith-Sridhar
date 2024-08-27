import asyncio
import websockets
import json
import streamlit as st

def initialize_game_state():
    if 'board' not in st.session_state:
        st.session_state['board'] = [['' for _ in range(5)] for _ in range(5)]
    if 'players' not in st.session_state:
        st.session_state['players'] = {'A': [], 'B': []}
    if 'current_turn' not in st.session_state:
        st.session_state['current_turn'] = 'A'
    if 'is_game_over' not in st.session_state:
        st.session_state['is_game_over'] = False

def display_board(board):
    st.write("### Game Board")
    for row in board:
        cols = st.columns(5)
        for i, cell in enumerate(row):
            cols[i].markdown(
                f"<div style='width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; background-color: black; color: white; border: 1px solid white;'>{cell}</div>",
                unsafe_allow_html=True
            )

async def send_message(websocket, message):
    await websocket.send(json.dumps(message))
    response = await websocket.recv()
    return json.loads(response)

async def main():
    initialize_game_state()  
    
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        st.title("5x5 Game Board")

        player = st.sidebar.selectbox("Select Player", ["A", "B"])
        positions = st.sidebar.text_input("Enter Positions (comma separated, 5 positions)")
        if st.sidebar.button("Place Characters"):
            if positions:
                positions_list = positions.split(",")
                if len(positions_list) == 5:
                    response = await send_message(websocket, {'type': 'initialize', 'player': player, 'positions': positions_list})
                    if response['type'] == 'error':
                        st.error(response['message'])
                    else:
                        st.success("Characters placed successfully!")
                        for row in range(5):
                            for col in range(5):
                                if response['state']['board'][row][col]:
                                    st.session_state['board'][row][col] = response['state']['board'][row][col]
                        st.session_state['players'] = response['state']['players']  # Update player positions
                else:
                    st.error("Please enter exactly 5 positions.")

        char_to_move = st.sidebar.text_input("Enter Character to Move")
        direction = st.sidebar.selectbox("Select Direction", ["L", "R", "F", "B", "FL", "FR", "BL", "BR"])
        if st.sidebar.button("Move Character"):
            if char_to_move:
                response = await send_message(websocket, {'type': 'move', 'player': player, 'char': char_to_move, 'direction': direction})
                if response['type'] == 'error':
                    st.error(response['message'])
                else:
                    st.success("Character moved successfully!")
                    st.session_state['board'] = response['state']['board']  
                    st.session_state['players'] = response['state']['players'] 

        display_board(st.session_state['board'])

        if st.session_state['is_game_over']:
            st.write(f"Game Over: {response.get('message', 'No message')}")
            
if __name__ == "__main__":
    asyncio.run(main())
