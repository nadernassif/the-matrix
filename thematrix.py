#!/usr/bin/env python3
import curses
import random
import time
import locale

# Enable Unicode support
locale.setlocale(locale.LC_ALL, '')

# Katakana range (used in the Matrix movie)
KATAKANA = [chr(i) for i in range(0x30A0, 0x30FF)]
LATIN = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()")
CHARS = LATIN + KATAKANA
FAIL_TEXT = "Matrix Failure"

def matrix(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    sh, sw = stdscr.getmaxyx()
    
    # Each column has its own state
    columns = []
    for i in range(sw):
        columns.append({
            'y': random.randint(-sh, 0),  # Start position (can be off-screen)
            'speed': random.choice([1, 2]),  # How fast it falls
            'length': random.randint(5, 25),  # Trail length
            'chars': [random.choice(CHARS) for _ in range(sh)]  # Pre-generate characters
        })
    
    paused = False
    draining = False
    drain_start = 0
    
    while True:
        sh, sw = stdscr.getmaxyx()
        
        # Handle terminal resize
        while len(columns) < sw:
            columns.append({
                'y': random.randint(-sh, 0),
                'speed': random.choice([1, 2]),
                'length': random.randint(5, 25),
                'chars': [random.choice(CHARS) for _ in range(sh)]
            })
        if len(columns) > sw:
            columns = columns[:sw]
        
        key = stdscr.getch()
        
        if key == ord(' '):
            if not paused:
                paused = True
            elif paused and not draining:
                paused = False
                draining = True
                drain_start = time.time()
        elif key == ord('q'):
            break
        
        stdscr.erase()
        
        if draining:
            # Drain effect - continue falling but gradually shorten trails
            all_done = True
            for col in columns:
                col['y'] += col['speed']  # Continue falling down
                # Gradually shorten the trail
                if col['length'] > 0:
                    col['length'] -= 1
                    all_done = False
            
            # Draw the draining columns
            for x, col in enumerate(columns):
                for i in range(col['length']):
                    y = col['y'] - i
                    if 0 <= y < sh:
                        char_idx = y % len(col['chars'])
                        char = col['chars'][char_idx]
                        try:
                            if i == 0:
                                stdscr.addstr(y, x, char, curses.color_pair(2) | curses.A_BOLD)
                            elif i < 3:
                                stdscr.addstr(y, x, char, curses.color_pair(1) | curses.A_BOLD)
                            else:
                                stdscr.addstr(y, x, char, curses.color_pair(1))
                        except:
                            pass
            
            # Check if drain is complete (all trails gone or enough time passed)
            if all_done or time.time() - drain_start > 5:
                # Reset after drain
                draining = False
                for col in columns:
                    col['y'] = random.randint(-sh, 0)
                    col['speed'] = random.choice([1, 2])
                    col['length'] = random.randint(5, 25)
                    col['chars'] = [random.choice(CHARS) for _ in range(sh)]
        
        elif not paused:
            # Normal falling effect
            for x, col in enumerate(columns):
                # Move the column down
                col['y'] += col['speed']
                
                # Reset if it's gone off screen
                if col['y'] > sh + col['length']:
                    col['y'] = random.randint(-sh, -5)
                    col['speed'] = random.choice([1, 2])
                    col['length'] = random.randint(5, 25)
                    col['chars'] = [random.choice(CHARS) for _ in range(sh)]
                
                # Draw the trail
                for i in range(col['length']):
                    y = col['y'] - i
                    if 0 <= y < sh:
                        char_idx = y % len(col['chars'])
                        char = col['chars'][char_idx]
                        
                        try:
                            if i == 0:
                                # Head - bright white
                                stdscr.addstr(y, x, char, curses.color_pair(2) | curses.A_BOLD)
                            elif i < 3:
                                # Near head - bright green
                                stdscr.addstr(y, x, char, curses.color_pair(1) | curses.A_BOLD)
                            else:
                                # Trail - normal green
                                stdscr.addstr(y, x, char, curses.color_pair(1))
                        except:
                            pass
        
        else:
            # Paused - draw frozen matrix
            for x, col in enumerate(columns):
                for i in range(col['length']):
                    y = col['y'] - i
                    if 0 <= y < sh:
                        char_idx = y % len(col['chars'])
                        char = col['chars'][char_idx]
                        try:
                            stdscr.addstr(y, x, char, curses.color_pair(1))
                        except:
                            pass
            
            # Draw popup box
            box_width = len(FAIL_TEXT) + 6
            box_height = 5
            start_y = max(0, sh // 2 - box_height // 2)
            start_x = max(0, sw // 2 - box_width // 2)
            
            # Draw background
            for y in range(box_height):
                for x in range(box_width):
                    try:
                        stdscr.addstr(start_y + y, start_x + x, " ", curses.color_pair(1))
                    except:
                        pass
            
            # Draw text
            try:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(start_y + 2, start_x + 3, FAIL_TEXT)
                stdscr.attroff(curses.A_REVERSE)
            except:
                pass
        
        stdscr.refresh()

def main():
    try:
        curses.wrapper(matrix)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()