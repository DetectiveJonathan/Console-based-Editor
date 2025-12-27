"""
Console-Based Multi-Line Editor
A simple editor supporting multi-line operations via text commands.
"""
import re


# Global Variables
lines = []  # List of lines, starts empty
line_cursor = 0  # Current line index (adjusted when lines are added/removed)
row_cursor = 0  # Current character position in line
show_line_cursor = False  # Toggle for line cursor display
show_row_cursor = False  # Toggle for row cursor display
copied_line = None  # Stores copied line for pasting
command_stack = []  # History of commands for undo



def display_help():
    """Display help information exactly as specified in the scope."""
    help_text = """? – display this help info
    . – toggle row cursor on and off
    ; – toggle line cursor on and off
    h – move cursor left
    j – move cursor up
    k – move cursor down
    l – move cursor right
    ^ – move cursor to beginning of the line
    $ – move cursor to end of the line
    w – move cursor to beginning of next word
    b – move cursor to beginning of previous word
    i – insert <text> before cursor
    a – append <text> after cursor
    x – delete character at cursor
    dw – delete word and trailing spaces at cursor
    yy – copy current line to memory
    p – paste copied line(s) below line cursor
    P – paste copied line(s) above line cursor
    dd – delete line
    o – insert empty line below
    O – insert empty line above
    u – undo previous command
    r – repeat last command
    s – show content
    q – quit program"""
    print(help_text)

def ensure_line_exists():
    """Ensure at least one line exists, adding an empty line if necessary."""
    global line_cursor

    if not lines:
        lines.append('')
        line_cursor = 0

def toggle_row_cursor():
    """Toggle visibility of the row cursor."""
    global show_row_cursor
    show_row_cursor = not show_row_cursor
    command_stack.append(('.',''))

def toggle_line_cursor():
    """Toggle visibility of the line cursor."""
    global show_line_cursor
    show_line_cursor = not show_line_cursor
    command_stack.append((';',''))


def move_left():
    """Move cursor left, if possible."""
    global row_cursor

    if row_cursor > 0:
        row_cursor -= 1

    command_stack.append(('h',''))

def move_right():
    """Move cursor right, within current line length."""
    global lines, row_cursor, line_cursor
    current_line = lines[line_cursor]

    if row_cursor < len(current_line) - 1:
        row_cursor += 1

    command_stack.append(('l', ''))

def move_up():
    """Move cursor up, adjusting row position if needed."""
    global lines, line_cursor, row_cursor
    original_row_cursor = row_cursor

    if line_cursor > 0:
        row_cursor = min(row_cursor, len(lines[line_cursor - 1]) - 1)
        line_cursor -= 1

    command_stack.append(('j', original_row_cursor))

def move_down():
    """Move cursor down, adjusting row position if needed."""
    global lines, line_cursor, row_cursor
    original_row_cursor = row_cursor

    if line_cursor < len(lines) - 1:
        if lines[line_cursor + 1] == '':
            line_cursor += 1
            row_cursor = 0
        else:
            row_cursor = min(row_cursor, len(lines[line_cursor + 1]) - 1)
            line_cursor += 1

    command_stack.append(('k', original_row_cursor))

def move_line_start():
    """Move cursor to the start of the current line."""
    global row_cursor
    original_row_cursor = row_cursor
    row_cursor = 0
    command_stack.append(('^', original_row_cursor))

def move_line_end():
    """Move cursor to the end of the current line."""
    global lines, row_cursor, line_cursor
    original_row_cursor = row_cursor
    row_cursor = len(lines[line_cursor]) - 1
    command_stack.append(('$', original_row_cursor))


def move_prev_word_start():
    """Move cursor to the start of the previous word."""
    global row_cursor, line_cursor, command_stack

    original_row = row_cursor
    line = lines[line_cursor]
    command_stack.append(('b', original_row))

    if not line:
        return

    matches = list(re.finditer(r'\S+', line))
    word_spans = [(m.start(), m.end()) for m in matches]

    # Find if cursor is inside a word
    for start, end in reversed(word_spans):
        if start < original_row < end:
            row_cursor = start
            return

    # Find the largest start <= original_row
    prev_starts = [start for start, _ in word_spans if start < original_row]
    if prev_starts:
        row_cursor = max(prev_starts)

def move_next_word_start():
    """Move cursor to the start of the next word."""
    global row_cursor, line_cursor, command_stack

    original_row = row_cursor
    line = lines[line_cursor] if line_cursor < len(lines) else ''
    command_stack.append(('w', original_row))

    if not line:
        return

    matches = list(re.finditer(r'\S+', line))
    next_starts = [m.start() for m in matches if m.start() > original_row]

    if next_starts:
        row_cursor = min(next_starts)

def insert_text(text):
    """Insert text before the cursor and update position."""
    global lines, row_cursor, line_cursor
    ensure_line_exists()
    line = lines[line_cursor]

    if line == '':
        lines[line_cursor] = text
        cursor = 0
        command_stack.append(('i1', text))
    else:
        lines[line_cursor] = line[:row_cursor] + text + line[row_cursor:]
        command_stack.append(('i2', text))

def append_text(text):
    """Append text after the cursor and update position."""
    global lines, row_cursor, line_cursor
    ensure_line_exists()
    line = lines[line_cursor]

    if line == '':
        lines[line_cursor] = text
        row_cursor = len(text) - 1
        command_stack.append(('a1', text))
    else:
        lines[line_cursor] = line[:row_cursor + 1] + text + line[row_cursor + 1:]
        row_cursor += len(text)
        command_stack.append(('a2', text))

def delete_char():
    """Delete the character at the cursor."""
    global lines, row_cursor, line_cursor
    line = lines[line_cursor]
    deleted_char = line[row_cursor]

    if line:
        if row_cursor < len(line) - 1:
            lines[line_cursor] = line[:row_cursor] + line[row_cursor + 1:]
            command_stack.append(('x1', deleted_char))
        else:
            lines[line_cursor] = line[:row_cursor]
            row_cursor -= 1
            command_stack.append(('x2', deleted_char))

def delete_word():
    """Delete from cursor to end of word and trailing spaces."""
    global lines, row_cursor, line_cursor, command_stack

    original_line = lines[line_cursor]
    original_row = row_cursor
    command_stack.append(('dw', original_line, original_row))

    # Find next word start or end of line
    matches = list(re.finditer(r'\S+', original_line))
    next_starts = [m.start() for m in matches if m.start() > original_row]
    if next_starts:
        end_pos = min(next_starts)
        lines[line_cursor] = original_line[:original_row] + original_line[end_pos:]
    else:
        lines[line_cursor] = original_line[:row_cursor]
        row_cursor -= 1

def copy_line():
    """Copy the current line to buffer."""
    global lines, copied_line
    copied_line = lines[line_cursor]

def paste_above():
    """Paste copied line above current line."""
    global lines, line_cursor, row_cursor
    original_row_cursor = row_cursor

    if copied_line is not None:
        lines.insert(line_cursor, copied_line)
        if copied_line == '':
            row_cursor = 0
        else:
            row_cursor = min(row_cursor, len(copied_line) - 1)

    command_stack.append(('P', original_row_cursor, copied_line))

def paste_below():
    """Paste copied line below current line."""
    global lines, line_cursor, row_cursor
    original_row_cursor = row_cursor

    if line_cursor < len(lines) - 1:
        lines.insert(line_cursor + 1, copied_line)
        move_down()
    else:
        lines.append(copied_line)
        move_down()

    command_stack.append(('p', original_row_cursor, copied_line))

def delete_line():
    """Delete the current line and adjust cursors."""
    global lines, line_cursor, row_cursor
    original_row_cursor = row_cursor

    if line_cursor < len(lines) - 1:
        command_stack.append(('dd1', lines[line_cursor], original_row_cursor))
        row_cursor = min(row_cursor, len(lines[line_cursor + 1]) - 1)
        lines.remove(lines[line_cursor])
    else:
        command_stack.append(('dd2', lines[line_cursor], original_row_cursor))
        row_cursor = min(row_cursor, len(lines[line_cursor - 1]) - 1)
        lines.remove(lines[line_cursor])
        line_cursor -= 1


def insert_empty_line_below():
    """Insert empty line below current line."""
    global lines, row_cursor, line_cursor
    original_row_cursor = row_cursor

    if line_cursor == len(lines) - 1:
        lines.append('')
        move_down()
    else:
        lines.insert(line_cursor + 1, '')
        move_down()

    command_stack.append(('o', original_row_cursor))

def insert_empty_line_above():
    """Insert empty line above current line."""
    lines.insert(line_cursor, '')
    original_row_cursor = row_cursor
    command_stack.append(('O', original_row_cursor))

def quit():
    global running
    running = False

def undo_last():
    """Revert the last command if possible."""
    global command_stack,show_row_cursor,show_line_cursor,row_cursor,line_cursor,lines

    if command_stack:
        cmd = command_stack.pop()
        if cmd[0] == '.':
            show_row_cursor = not show_row_cursor
        elif cmd[0] == ';':
            show_line_cursor = not show_line_cursor
        elif cmd[0] == 'h':
            row_cursor += 1
        elif cmd[0] == 'l':
            row_cursor -= 1
        elif cmd[0] == 'j':
            line_cursor += 1
            row_cursor = cmd[1]
        elif cmd[0] == 'k':
            line_cursor -= 1
            row_cursor = cmd[1]
        elif cmd[0] == '^':
            row_cursor = cmd[1]
        elif cmd[0] == '$':
            row_cursor = cmd[1]
        elif cmd[0] == 'b':
            row_cursor = cmd[1]
        elif cmd[0] == 'w':
            row_cursor = cmd[1]
        elif cmd[0] == 'i1':
            lines[line_cursor] = ''
        elif cmd[0] == 'i2':
            line = lines[line_cursor]
            lines[line_cursor] = line[:row_cursor] + line[row_cursor + len(cmd[1]):]
        elif cmd[0] == 'a1':
            lines[line_cursor] = ''
            row_cursor = 0
        elif cmd[0] == 'a2':
            line = lines[line_cursor]
            lines[line_cursor] = line[:row_cursor - len(cmd[1]) + 1] + line[row_cursor + 1:]
            row_cursor -= len(cmd[1])
        elif cmd[0] == 'x1':
            line = lines[line_cursor]
            lines[line_cursor] = line[:row_cursor] + cmd[1] + line[row_cursor:]
        elif cmd[0] == 'x2':
            lines[line_cursor] = lines[line_cursor] + cmd[1]
            row_cursor += 1
        elif cmd[0] == 'dw':
            lines[line_cursor] = cmd[1]
            row_cursor = cmd[2]
        elif cmd[0] == 'P':
            delete_line()
            row_cursor = cmd[1]
        elif cmd[0] == 'p':
            delete_line()
            row_cursor = cmd[1]
            line_cursor -= 1
        elif cmd[0] == 'dd1':
            lines.insert(line_cursor, cmd[1])
            row_cursor = cmd[2]
        elif cmd[0] == 'dd2':
            lines.append(cmd[1])
            line_cursor += 1
            row_cursor = cmd[2]
        elif cmd[0] == 'o':
            lines.remove(lines[line_cursor])
            line_cursor -= 1
            row_cursor = cmd[1]
        elif cmd[0] == 'O':
            lines.remove(lines[line_cursor])
            row_cursor = cmd[1]


def repeat_last():
    """Repeat the last valid command."""
    if command_stack:
        last_command = command_stack[-1]
        if last_command[0] == '.':
            toggle_row_cursor()
        elif last_command[0] == ';':
            toggle_line_cursor()
        elif last_command[0] == 'h':
            move_left()
        elif last_command[0] == 'l':
            move_right()
        elif last_command[0] == 'j':
            move_up()
        elif last_command[0] == 'k':
            move_down()
        elif last_command[0] == '^':
            move_cursor_to_start_of_line()
        elif last_command[0] == '$':
            move_cursor_to_end_of_line()
        elif last_command[0] == 'b':
            move_prev_word_start()
        elif last_command[0] == 'w':
            move_next_word_start()
        elif last_command[0] == 'i1' or last_command[0] == 'i2':
            insert_text(last_command[1])
        elif last_command[0] == 'a1' or last_command[0] == 'a2':
            append_text(last_command[1])
        elif last_command[0] == 'x1' or last_command[0] == 'x2':
            delete_char()
        elif last_command[0] == 'dw':
            delete_word()
        elif last_command[0] == 'P':
            paste_above(last_command[2])
        elif last_command[0] == 'p':
            paste_below(last_command[2])
        elif last_command[0] == 'dd1' or last_command[0] == 'dd2':
            delete_line()
        elif last_command[0] == 'o':
            insert_empty_line_below()
        elif last_command[0] == 'O':
            insert_empty_line_above()

def show_content():
    """Display current editor content with cursors."""
    global lines, line_cursor,row_cursor,show_row_cursor,show_line_cursor

    if lines:
        if show_line_cursor is True:
            for i in range(len(lines)):
                if i == line_cursor:
                    if show_row_cursor is True:
                        before = lines[i][:row_cursor] if lines[i] != '' else ''
                        after = lines[i][row_cursor + 1:] if len(lines[i]) > 1 else ''
                        cursor = lines[i][row_cursor] if lines[i] != '' else ''
                        print('*' + f"{before}\033[42m{cursor}\033[0m{after}")
                    else:
                        print('*' + lines[i])
                else:
                    print(' ' + lines[i])
        else:
            for i in range(len(lines)):
                if i == line_cursor:
                    if show_row_cursor is True:
                        before = lines[i][:row_cursor] if lines[i] != '' else ''
                        if row_cursor < len(lines[i]) - 1:
                            after = lines[i][row_cursor + 1:]
                        else:
                            after = ''
                        cursor = lines[i][row_cursor] if lines[i] != '' else ''
                        print(f"{before}\033[42m{cursor}\033[0m{after}")
                    else:
                        print(lines[i])
                else:
                    print(lines[i])

valid_commands = ['?','.',';','h',
                  'j','k','l','^',
                  '$','b','w','x',
                  'dw','yy','p','P',
                  'dd','o','O','u',
                  'r','s','q']

def parse_input(user_input):
    """Parse user input into command and text."""
    if user_input in valid_commands:
        return True

    else:
        if user_input.startswith('i') or user_input.startswith('a'):
            return True
        else:
            return False

def main():
    """Main loop to process user commands."""
    global copied_line

    while True:
        user_input = input('>')
        cmd = user_input
        if parse_input(user_input):
            if cmd == '?':
                display_help()
            elif cmd == '.':
                toggle_row_cursor()
                show_content()
            elif cmd == ';':
                toggle_line_cursor()
                show_content()
            elif cmd == 'h':
                move_left()
                show_content()
            elif cmd == 'l':
                move_right()
                show_content()
            elif cmd == 'j':
                move_up()
                show_content()
            elif cmd == 'k':
                move_down()
                show_content()
            elif cmd == '^':
                move_line_start()
                show_content()
            elif cmd == '$':
                move_line_end()
                show_content()
            elif cmd == 'b':
                move_prev_word_start()
                show_content()
            elif cmd == 'w':
                move_next_word_start()
                show_content()
            elif cmd.startswith('i'):
                insert_text(cmd[1:])
                show_content()
            elif cmd.startswith('a'):
                append_text(cmd[1:])
                show_content()
            elif cmd == 'x':
                delete_char()
                show_content()
            elif cmd == 'dw':
                delete_word()
                show_content()
            elif cmd == 'yy':
                copied_line = lines[line_cursor]
                show_content()
            elif cmd == 'P':
                paste_above()
                show_content()
            elif cmd == 'p':
                paste_below()
                show_content()
            elif cmd == 'dd':
                delete_line()
                show_content()
            elif cmd == 'o':
                insert_empty_line_below()
                show_content()
            elif cmd == 'O':
                insert_empty_line_above()
                show_content()
            elif cmd == 'u':
                undo_last()
                show_content()
            elif cmd == 'r':
                repeat_last()
                show_content()
            elif cmd == 's':
                show_content()
            elif cmd == 'q':
                break
        else:
            continue


if __name__ == "__main__":
    main()
