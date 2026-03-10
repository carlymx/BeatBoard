# BeatBoard User Manual

![main](../../imgs/beatboard_002.png)

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Managing Beats](#managing-beats)
5. [Connections Between Beats](#connections-between-beats)
6. [Canvas Tools](#canvas-tools)
7. [Customization](#customization)
8. [Export and Save](#export-and-save)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

BeatBoard is a virtual desktop whiteboard application for writers, inspired by Final Draft Beat Board. It is a tool especially designed for screenwriters, short story writers, and novelists who need to visualize the structure of their stories.

With BeatBoard you can:
- Create an infinite canvas to organize your ideas
- Create beat cards with title and content
- Connect beats with curved flow lines
- Visually organize and reorder your elements
- Customize the appearance with themes and colors
- Export your work to PDF or text

---

## Getting Started

### Installation

To run BeatBoard:

1. **From source code**:
   ```bash
   cd BeatBoard
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate  # Windows
   pip install pyside6
   python -m beatboard.app.main
   ```

2. **Pre-compiled executable**:
   Download the executable file from the releases page and run it directly.

### Create your First Project

When you start BeatBoard, a blank project is automatically created. You can immediately start creating beats on the canvas.

To save your project:
1. Go to **File > Save** (or press **Ctrl+S**)
2. Choose the location and name for your file
3. BeatBoard projects have the `.bbp` extension

---

## User Interface

![beatboard_interface](../../imgs/manual/0001.png)

The BeatBoard interface is divided into the following areas:

### Toolbar

![beatboard_interface](../../imgs/manual/0002.png)

The toolbar provides quick access to the most frequently used functions:

| Button | Function | Shortcut |
|--------|----------|----------|
| New | Create new project | Ctrl+N |
| Open | Open existing project | Ctrl+O |
| Save | Save project | Ctrl+S |
| + (Zoom In) | Increase zoom | Ctrl++ |
| - (Zoom Out) | Decrease zoom | Ctrl+- |
| Zoom | Area selection zoom | Z |
| Fit | Fit view to content | Ctrl+0 |
| Center | Center view on origin | - |
| Connect | Activate connection mode | C |

### Properties Panel

![beatboard_interface](../../imgs/manual/0003.png)

The properties panel (located on the right) allows you to edit the selected element:

- **No beat selected**: Shows a message indicating "Nothing selected"
- **One beat selected**: Allows editing title, content, color, and title visibility
- **Multiple beats selected**: Allows editing common properties for all of them
- **Selected connection**: Allows editing color, line thickness, node shape, and label

### Status Bar

The bottom bar displays useful information:
- Number of beats in the project
- Current zoom level
- Project status (Modified/Saved)
- Cursor position on the canvas

---

## Managing Beats

![beatboard_interface](../../imgs/manual/0004.png)

### Create a Beat

**Method 1 - Double click**:
1. Double-click on any empty area of the canvas
2. A new beat will be created at that position

### Edit a Beat

![beatboard_interface](../../imgs/manual/0005.png)

**Quick editing**:
1. Double-click on the beat you want to edit
2. The beat editing dialog will open

![beatboard_interface](../../imgs/manual/0006.png)

**Editing from the properties panel**:
1. Select the beat
2. Modify the title or content directly in the properties panel
3. Changes are applied automatically

**Full editor**:
1. Select the beat
2. In the properties panel, click "Open full editor"
3. The dialog with advanced formatting options will open

### The Beat Editor

The beat editor offers the following formatting tools:

#### Format Bar
- **B** (Bold): Apply bold formatting to selected text
- *I* (Italic): Apply italic formatting
- **U** (Underline): Apply underline formatting
- **Font size**: Font size selector (8-32pt)
- **H1, H2, H3**: Insert headings of different levels
- **•** (Bullet points): Insert bullet list
- **A** (Text color): Change color of selected text
- **█** (Highlight): Apply background color to text
- **[Link]**: Insert hyperlink
- **[Code]**: Insert text with code formatting
- **[Quote]**: Insert quote

#### Editor Fields
- **Title**: Beat name (optional)
- **Content**: Detailed beat description (supports rich formatting)
- **Color**: Beat color selector

### Move a Beat

1. Click on the beat
2. Drag the beat to the new position
3. Release the mouse button

### Multiple Selection

**Select multiple beats**:
- Hold **Ctrl** while clicking on each beat
- Or drag a selection rectangle around the desired beats

**Move multiple beats**:
1. Select multiple beats
2. Drag any of them
3. All selected beats will move together

### Copy and Paste

- **Copy**: Select the beat and press **Ctrl+C**
- **Cut**: Select the beat and press **Ctrl+X**
- **Paste**: Press **Ctrl+V** to create a copy in the center of the canvas

### Delete a Beat

1. Select the beat (or beats)
2. Press **Delete** or **Supr** or with **right-click > Delete**

### Z-Order (Depth)

![beatboard_interface](../../imgs/manual/0007.png)

BeatBoard allows you to control which beats appear in front of others:

| Action | Shortcut | Description |
|--------|----------|-------------|
| Bring to front | Ctrl+Home | Moves the beat to the top layer |
| Send to back | Ctrl+End | Moves the beat to the bottom layer |
| Move up | Ctrl+PageUp | Swaps position with the beat immediately above |
| Move down | Ctrl+PageDown | Swaps position with the beat immediately below |

### Beat Colors

![beatboard_interface](../../imgs/manual/0008.png)

BeatBoard offers 10 predefined colors and 3 customizable:

| Key | Color |
|-----|-------|
| 1 | Yellow |
| 2 | Blue |
| 3 | Green |
| 4 | Red |
| 5 | Orange |
| 6 | Purple |
| 7 | Gray |
| 8 | Customizable 1 |
| 9 | Customizable 2 |
| 0 | Customizable 3 |

**Change color with keyboard**:
1. Select one or several beats
2. Press a key from 1 to 0

**Customize colors**:
1. Select a beat and open the **Full editor**
2. Double-click on one of the three customizable colors and edit it

---

## Connections Between Beats

![beatboard_interface](../../imgs/manual/0009.png)

Connections are curved lines that join two beats, showing the flow of the story.

### Create a Connection

**Method 1 - Toolbar**:
1. Click the "Connect" button on the toolbar (or press **C**)
2. The cursor will change to a cross
3. Click on the source beat
4. Click on the destination beat
5. The connection will be created automatically
6. Press **Escape** to exit connection mode

**Note**: When connection mode is active, a banner appears at the bottom of the canvas indicating "Connection Mode Activated".

### Edit a Connection

**Select connection**:
- Click directly on the connection line
- The connection will be highlighted with a blue border

![beatboard_interface](../../imgs/manual/0010.png)

**Connection properties** (in the properties panel):
- **Color**: Line color (red, blue, green, yellow, orange, purple, dark gray)
- **Thickness**: Line thickness (0.5 - 10 px)
- **Node shape**: Shape of the terminator at the ends:
  - Circle
  - Square
  - Arrow
  - None
- **Label**: Text that appears in the center of the connection

### Editable Nodes

![beatboard_interface](../../imgs/manual/0011.png)

Connections have control points that allow you to modify their curvature:

1. Select the connection
2. Two handles (points) will appear on the line
3. Drag the handles to adjust the curve
4. Double-click on a handle to reset to default curvature

### Delete a Connection

1. Select the connection
2. Press **Delete** or **Supr**

---

## Canvas Tools

### Zoom

**Zoom in**:
- Go to **View > Zoom In**
- Press **Ctrl++**
- Or use the "+" button on the toolbar

**Zoom out**:
- Go to **View > Zoom Out**
- Press **Ctrl+-**
- Or use the "-" button on the toolbar

**Fit to content**:
- Go to **View > Fit to Content**
- Press **Ctrl+0**
- Or use the fit button on the toolbar

**Area selection zoom**:
1. Press **Z** or click the zoom button on the toolbar
2. Drag a rectangle around the area you want to see
3. The view will center and adjust to the selected area
4. Press **Escape** to cancel

### Panning

**With keyboard**:
- Hold down the **Space** key
- Drag the mouse to move the canvas

**With mouse**:
- Hold down the mouse's middle button
- Drag to move the canvas

### Grid

The grid helps visually align beats.

**Show/Hide**:
- Go to **View > Show Grid**
- Or use the configured shortcut

**Customize grid**:
1. Go to **View > Grid Options**
2. **Cell size**: Choose between 50, 100, 150, 200 or 250 px
3. **Grid color**: 
   - Auto: Adapts to theme
   - Predefined colors: Yellow, Blue, Green, Red, Orange, Purple, Gray
   - Custom: Choose your own color

### Center Point

![beatboard_interface](../../imgs/manual/0012.png)

The center point (origin 0,0) is shown as a small cross in the center of the canvas. Click the "Center" button on the toolbar to move the view to the origin.

---

## Customization

### Themes

BeatBoard offers 9 different themes:

**Light themes**:
- Light (default)
- Solarized Light
- GitHub Light
- PaperColor

**Dark themes**:
- Dark (default)
- Dracula
- Nord
- One Dark
- Material Dark

**Apply theme**:
1. Go to **Preferences > Theme**
2. Select the desired theme
3. You can also choose "System" to use your operating system's theme

### Canvas Background Color

You can customize the canvas background color:

1. Go to **Preferences > Background Color**
2. Choose from:
   - White
   - Light Gray
   - Gray
   - Dark Gray
   - Cream
   - Dark
   - Black
   - Custom (choose your own color)

**Reset theme colors**:
- Select "Reset theme colors" to return to the current theme's default colors

### Remember Defaults

Enable the option **"Remember size and color of last beat"** in Preferences so that new beats inherit the size and color of the last beat created.

### Language

BeatBoard is available in 4 languages:
- English
- Spanish (Español)
- French (Français)
- German (Deutsch)

To change the language:
1. Go to **Preferences > Language**
2. Select the desired language
3. Restart the application to apply the change

### Spell Check

BeatBoard includes an integrated spell checker:

**Activate**:
1. Go to **Preferences > Spell Check > Enable Spell Check**

**Dictionary language**:
1. Go to **Preferences > Spell Check > Dictionary Language**
2. Select the language: English, Spanish, French, or German

**Using the spell checker**:
- Incorrect words will be underlined in red
- Right-click on a word to see suggestions

---

## Export and Save

### File Format

BeatBoard projects are saved in `.bbp` format (JSON). This format includes:
- All beats (title, content, position, size, color)
- All connections
- Canvas settings

### Save Project

- **Save**: **Ctrl+S** (saves to current file)
- **Save as**: **Ctrl+Shift+S** (choose location and name)

### Export to PDF

- Under development

### Export to Text

1. Go to **File > Export to Text**
2. Select the location and name for the file
3. A text file with all beats will be generated

### Recent Files

BeatBoard maintains a list of the last 10 opened files:

1. Go to **File > Open Recent**
2. Select the desired file

If a file in the list no longer exists, you will be asked if you want to remove it from the list.

### Auto-Save

BeatBoard can automatically save your project:

1. Go to **Preferences > Backup Options**
2. Configure:
   - **Backup on open**: Creates a copy when opening the project
   - **Auto-save**: Enable/disable automatic saving
   - **Interval**: How often to save (1, 2, 5, 10, 15, or 30 minutes)
   - **Maximum backups**: Number of backups to keep

---

## Keyboard Shortcuts

### File

| Shortcut | Function |
|----------|----------|
| Ctrl+N | New project |
| Ctrl+O | Open project |
| Ctrl+S | Save project |
| Ctrl+Shift+S | Save as |
| Ctrl+W | Close project |
| Ctrl+Q | Exit |

### Edit

| Shortcut | Function |
|----------|----------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+A | Select all |
| Ctrl+C | Copy |
| Ctrl+X | Cut |
| Ctrl+V | Paste |
| Delete | Delete selection |
| Ctrl+Home | Bring to front |
| Ctrl+End | Send to back |
| Ctrl+PageUp | Move up |
| Ctrl+PageDown | Move down |

### View

| Shortcut | Function |
|----------|----------|
| Ctrl++ | Zoom in |
| Ctrl+- | Zoom out |
| Ctrl+0 | Fit to content |
| Space | Pan mode (hold down) |

### Other Shortcuts

| Shortcut | Function |
|----------|----------|
| 1-0 | Change selection color |
| C | Toggle connection mode (no selection) |
| Z | Selection zoom (no selection) |
| Escape | Cancel / Deselect all |
| Double-click (canvas) | Create new beat |
| Double-click (beat) | Edit beat |

---

## Troubleshooting

### The program doesn't start

1. Make sure you have Python 3.10+ installed
2. Make sure you have installed PySide6: `pip install pyside6`
3. Check for any errors in the terminal

### Beats don't save

1. Make sure you have write permissions to the folder
2. Make sure to save the project before closing (Ctrl+S)
3. Check the project status in the status bar (should say "Saved")

### Grid doesn't show

1. Make sure the grid is enabled: **View > Show Grid**
2. Try changing the grid color in **View > Grid Options**

### Spell checker doesn't work

1. Make sure it's enabled in **Preferences > Spell Check**
2. Make sure you've selected the correct dictionary language

### Custom colors don't save

1. Custom colors are saved in preferences, not in the project
2. They are automatically applied to future beats according to the configuration

---

## Additional Information

### Mouse Shortcuts

- **Double-click on canvas**: Create new beat
- **Double-click on beat**: Edit beat
- **Single click**: Select element
- **Ctrl + Click**: Add to selection
- **Drag (selection)**: Create selection rectangle
- **Drag (beat)**: Move beat
- **Mouse wheel**: Zoom (with Ctrl pressed)
- **Middle mouse button**: Pan

### Glossary

- **Beat**: Individual card on the canvas representing a scene or moment in the story
- **Connection**: Curved line that joins two beats
- **Canvas**: The work area where beats are placed
- **Z-Order**: Depth or layer of an element (what appears on top of what)
- **Theme**: Set of colors and styles that define the application's appearance
- **Properties panel**: Side panel where the properties of the selected element are edited

---

## Credits

BeatBoard was created by CarlyMx and is inspired by Final Draft Beat Board.

For more information, updates, and support, visit the GitHub repository.

---

*Manual created for BeatBoard version 1.0.27*
