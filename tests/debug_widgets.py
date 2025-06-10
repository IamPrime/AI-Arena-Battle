import streamlit as st
from streamlit.testing.v1 import AppTest

def debug_arena_widgets():
    """Debug script to see available widgets in Arena.py"""
    at = AppTest.from_file("Arena.py")
    at.run()
    
    print("=== Available Widgets ===")
    print(f"Text inputs: {len(at.text_input)}")
    for i, input_widget in enumerate(at.text_input):
        print(f"  [{i}] Key: '{input_widget.key}', Label: '{input_widget.label}'")
    
    print(f"Buttons: {len(at.button)}")
    for i, button in enumerate(at.button):
        print(f"  [{i}] Key: '{button.key}', Label: '{button.label}'")
    
    print(f"Selectboxes: {len(at.selectbox)}")
    for i, select in enumerate(at.selectbox):
        print(f"  [{i}] Key: '{select.key}', Label: '{select.label}'")

if __name__ == "__main__":
    debug_arena_widgets()