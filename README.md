# Console-Based Multi-Line Editor

A Python-based command-line text editor that supports multi-line operations, global state management, and a comprehensive undo history. This project implements a modal editing style similar to Vim, utilizing command-based navigation and manipulation.

## 📋 Features

* **Multi-line Editing:** Create, append, insert, and delete text across multiple lines.
* **Vim-like Navigation:** Navigate using `h`, `j`, `k`, `l` and word-based jumps (`w`, `b`).
* **Clipboard Buffer:** Copy (`yy`) and paste (`p`/`P`) entire lines.
* **Undo History:** Stack-based undo system (`u`) that tracks all state changes.
* **Visual Feedback:** Toggleable line and row cursors with ANSI color highlighting.
* **RegEx Word Parsing:** Robust word navigation using regular expressions.

## 🛠 Installation & Usage

### Prerequisites
* Python 3.x
* No external dependencies required (uses standard `re` library).

### Running the Editor
1.  Clone the repository:
    ```bash
    git clone [https://github.com/DetectiveJonathan/Console-based-Editor.git](https://github.com/DetectiveJonathan/Console-based-Editor.git)
    ```
2.  Navigate to the directory and run the script:
    ```bash
    python "Console-based Editor.py"
    ```

## 🎮 Command Cheat Sheet

The editor operates via a command loop. Type a command and press `Enter`.

### Navigation
| Command | Action |
| :--- | :--- |
| `h` / `l` | Move cursor **Left** / **Right** |
| `j` / `k` | Move cursor **Up** / **Down** |
| `w` | Move to beginning of **next word** |
| `b` | Move to beginning of **previous word** |
| `^` | Jump to **start** of line |
| `$` | Jump to **end** of line |

### Editing
| Command | Action |
| :--- | :--- |
| `i <text>` | **Insert** text before cursor |
| `a <text>` | **Append** text after cursor |
| `x` | Delete **character** at cursor |
| `dw` | Delete **word** and trailing spaces |
| `dd` | Delete current **line** |
| `o` | Insert empty line **below** |
| `O` | Insert empty line **above** |

### Clipboard & History
| Command | Action |
| :--- | :--- |
| `yy` | **Copy** current line to memory |
| `p` | **Paste** copied line *below* cursor |
| `P` | **Paste** copied line *above* cursor |
| `u` | **Undo** last command |
| `r` | **Repeat** last command |

### System
| Command | Action |
| :--- | :--- |
| `s` | **Show** current content |
| `.` | Toggle **Row** cursor visibility |
| `;` | Toggle **Line** cursor visibility |
| `?` | Display **Help** menu |
| `q` | **Quit** program |

## 💡 Usage Examples

Here are common workflows to illustrate the command logic.

### Scenario 1: Fixing a Typo
**Goal:** Change "Hellp World" to "Hello World".
1.  **Navigate:** Use `l` (right) to move the cursor to 'p'.
2.  **Delete:** Type `x` to delete 'p'. (Line becomes "Hell World")
3.  **Insert:** Type `i` then `o`. (Line becomes "Hello World")
4.  **Finish:** Press `Enter` to confirm the text insertion.

### Scenario 2: Moving Text (Cut & Paste)
**Goal:** Move the current line to the bottom of the file.
1.  **Cut:** Type `dd`. The line is deleted and saved to memory.
2.  **Move:** Type `j` or `k` to navigate to the bottom line.
3.  **Paste:** Type `p`. The deleted line is inserted below the current cursor position.

### Scenario 3: Bulk Deletion
**Goal:** Delete the next 3 words.
1.  **Delete One:** Type `dw` (Deletes word at cursor).
2.  **Repeat:** Type `r` (Repeats the delete word command).
3.  **Repeat:** Type `r` again.

## 🧠 Implementation Logic

### Data Structure: List-Based Grid
The editor avoids complex linked structures in favor of direct index access, ensuring $O(1)$ retrieval times.
* **The Grid (`lines`):** The document is stored as a global Python `List` of strings.
* **Coordinate System:** Position is tracked via two global integers:
    * `line_cursor`: Tracks the vertical index in the list.
    * `row_cursor`: Tracks the horizontal character index within the specific string.
* **Boundary Handling:** Movement functions (like `move_down`) dynamically check the length of the target line to prevent the cursor from exceeding string bounds.

### Undo Architecture (`command_stack`)
The Undo feature is implemented using a **Stack (LIFO)** data structure.
* **Delta Storage:** Rather than saving the full file state, the editor pushes a tuple containing the **Command ID** and **Metadata** (deleted text, previous coordinates) to the stack.
* **Reversal:** When `u` is invoked, the system pops the last tuple (e.g., `('x1', 'a')`) and performs the inverse operation (inserting 'a' back at the saved position).

### The Repeat Command (`r`)
The Repeat command allows for efficient workflow by reusing the logic of the previous action.
* **Stack Inspection:** It inspects `command_stack[-1]` to identify the last successful operation.
* **Function Dispatch:** Instead of simulating keystrokes, it re-invokes the specific function (e.g., `delete_word()`). This ensures that context-sensitive commands (like deleting a word) recalculate boundaries correctly based on the *new* cursor position.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
