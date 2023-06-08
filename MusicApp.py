#############################################################################################################
#   GOALS  
#############################################################################################################
#       Convert MIDI files to readable notes
#       Display sheet music
#       Create a virtual piano for user input


#############################################################################################################
#   Config  
#############################################################################################################
import turtle           # documentation: https://docs.python.org/3/library/turtle.html
import tkinter as tk    # resource: https://www.tutorialspoint.com/python/python_gui_programming.htm
                        # resource: https://compucademy.net/python-turtle-graphics-and-tkinter-gui-programming/ 
import ReadMidi         # created by me, utilizes the mido module: https://mido.readthedocs.io/en/latest/
import pygame.time      # for maintaining a consistent frames per second
import time             # https://www.tutorialspoint.com/python/time_sleep.htm

#   screen settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
window = turtle.Screen()
window.setup(WINDOW_WIDTH, WINDOW_HEIGHT)
window.title("Music App")
window.tracer(0) # turn off drawing animations
tk_canvas = window.getcanvas()

#   text
TURTLE_FONT = ('Times', 30, 'italic')
TK_FONT = ("Times", 18)

#   notes
NOTE_SIZE = 3         
NOTE_DISTANCE = NOTE_SIZE*5.91 # determines vertical distance of notes (one half-step)
clef = "trebleClef.gif" # PICTURE LINK: https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.stickpng.com%2Fimg%2Fmiscellaneous%2Fmusic-symbols%2Ftreble-clef&psig=AOvVaw1SAxxlXKXa-HLxdXcSqLAz&ust=1619571929178000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCPjJ-N6dnfACFQAAAAAdAAAAABAD
                        # Convert to GIF: https://ezgif.com/jpg-to-gif
keyboard_pic = "keyboard.gif" # http://clipart-library.com/clipart/8T6og5E8c.htm

#   file to store song information
CSV_FILE = "MidiFiles.csv"  # midi files created using https://onlinesequencer.net/ and https://signal.vercel.app/edit

def read_csv(file_name): 
    """get song data from csv file
    returns a list of lists 
    each element: [str file_name, str time_signature, int pickup, str key_signature, int song_number]"""
    file_obj = open(file_name)
    song_list = []
    for song_num, line in enumerate(file_obj): 
        if song_num != 0:
            contents = line.split(", ")
            contents[1] = [int(num) for num in contents[1].split("/")] # ex. turns "4/4" into [4,4]
            contents[2] = int(contents[2]) # pickup
            contents[-1] = contents[-1].strip("\n") # remove \n from last element
            contents.append(song_num)   # add song number
            song_list.append(contents)
    file_obj.close()
    return song_list


#############################################################################################################
#   GUI and Song Selection
#############################################################################################################

class Song_Selection():
    """Use a menu to choose a song"""
    def __init__(self, window, file_name):
        """Create frames and widgets for Song Selection box
        Frame: frame 
        Widgets: instructions, listbox, scrollbar"""

        # store a list of all the songs
        self.song_list = read_csv(file_name)
        self.song = None
        
        # menu button to go back to song selection
        self.menu_button = tk.Button(tk_canvas.master, bg="white", height=1, width=7, font=TK_FONT, text="Menu", border=0, activebackground="PaleGreen1", command=self.show)
        tk_canvas.create_window(400, -250, window=self.menu_button)

        # back button to go back to the song
        self.back_button = tk.Button(tk_canvas.master, bg="white", height=1, width=7, font=TK_FONT, text="Back", border=0, activebackground="PaleGreen1", command=self.hide)
        tk_canvas.create_window(400, -250, window=self.back_button)

        # song selection frame
        self.frame = tk.Frame(tk_canvas.master, bg="white")
        tk_canvas.create_window(0, 0, window=self.frame, width=1000, height=600)

        # instructions
        self.instructions = tk.Label(self.frame, bg="white", text="Choose a song to play: ", font=TK_FONT)
        self.instructions.grid(row=1, column=2, padx=WINDOW_WIDTH/2-125, pady=(100,10))

        # listbox to display the songs
        self.listbox = tk.Listbox(self.frame, bg="white", relief="flat", font=TK_FONT, highlightthickness=0)
        self.listbox.grid(row=2, column=2, ipadx=50, ipady=10)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_select)
        self.update_listbox()

        # scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", width=16, highlightthickness=0)
        self.scrollbar.grid(row=2, column=2, sticky="ns", padx=(325,0))
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)        

    def update_listbox(self):
        """Read the songs and put them in the listbox display"""
        self.listbox.delete('0','end') # erase entire listbox
        for song in self.song_list:
            song_name = song[0][0:len(song[0])-4]   # extract the song name from the midi file name
            song_name = song_name.split("_")
            self.listbox.insert("end", str(song[-1]) + ". " + " ".join(song_name))
        self.listbox.insert("end", "")
        self.listbox.insert("end","-- Click to add more songs --")

    def hide(self):
        """hides the song selection box behind the canvas"""
        self.frame.lower()
        self.scrollbar.lower()
        self.listbox.lower()
        self.instructions.lower()
        self.back_button.lower()

    def show(self):
        """displays the song selection box over the canvas for the user to choose a song"""
        self.frame.tkraise()
        self.scrollbar.tkraise()
        self.listbox.tkraise()
        self.instructions.tkraise() 
        self.back_button.tkraise()

    def listbox_select(self, event):
        """handle song selection box based on the selected choice"""
        selected_song = self.song_list[int(self.listbox.get("anchor")[0])-1]    # get the index from the song_list to find the song name
        self.hide()

        # delete previous turtle drawings  
        if (self.song is not None):
            self.song.clear()

        # initialize new song and play
        self.song = Song(selected_song)
        self.song.play()
        
        # when song is finished
        self.show()
    

#############################################################################################################
#   Sheet Music Display 
#############################################################################################################

def create_painter(x, y): 
    """Returns a painter (turtle) object at (x,y)"""
    painter = turtle.Turtle()
    painter.speed(0)
    painter.hideturtle()
    painter.penup()
    painter.pensize(3)
    painter.goto(x, y) 
    return painter

def draw_staff(clef_file):
    """Creates staff and clef
    clef_file is a .gif file"""
    staff = turtle.Turtle()
    staff.penup()
    staff.goto(-WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - NOTE_DISTANCE*15)
    staff.pensize(2)
    for _ in range(5): # use _ when the for loop variable is unused
        staff.pendown()
        staff.setx(-WINDOW_WIDTH/2)
        staff.setx(WINDOW_WIDTH/2)
        staff.penup()
        staff.sety(staff.ycor() + NOTE_DISTANCE*2)
    # draw treble clef
    staff.goto(-WINDOW_WIDTH/2.3, staff.ycor() - NOTE_DISTANCE*6.75)
    window.addshape(clef_file)
    staff.shape(clef_file)
    window.update()
    return staff

def get_y(pitch_num, key_signature): 
    """Returns the y coordinate based on the midi number"""
    mod_pitch_num = pitch_num % 12 # gets the note value out of 12 notes (C=0)
    # account for accidentals
    if mod_pitch_num in {1,3,6,8,10}: 
        if "sharp" in key_signature:
            pitch_num -= 1
        if "flat" in key_signature: 
            pitch_num += 1
    # account for half-steps on the staff
    octave = 2*(pitch_num//12 - 5) # uses C4 as octave=0
    if mod_pitch_num < 5:
        pitch_num -= 1
    if mod_pitch_num > 11:
        pitch_num += 1
    pitch_num += octave
    # adjust to fit window dimensions
    return (WINDOW_HEIGHT/2 + NOTE_DISTANCE*(pitch_num - 91)/2)- 3

def get_x(beat, time_signature, type): 
    """Returns the x coordinate based on the absolute time (measured in beats since the start)
    type must either be "note" or "barline" """
    distance = WINDOW_WIDTH/8
    beat = int(beat + 0.05) # round beat to an int

    x = -WINDOW_WIDTH/5 # position of the first beat
    for previous_beat in range(1,beat+1):
        x += distance # increment distance for every previous note
        if previous_beat % time_signature[0] == 0:
            x += distance # increment distance for every previous barline
    if type == "note":
        return x
    if type == "barline":
        return x - distance # subtract 1 distance because the distance was originally added to offset for the barline


class Song():
    """Store attributes of the selected song and play the song"""
    def __init__(self, selected_song):
        """initialize variables"""
        # info from csv file
        self.song_name = selected_song[0][0:len(selected_song[0])-4]
        self.time_signature = selected_song[1]
        self.pickup = selected_song[2]
        self.key_signature = selected_song[3] 

        self.song_name = self.song_name.split("_")
        self.song_name = " ".join(self.song_name)
        self.title = tk.Label(tk_canvas.master, bg="white", height=1, font=TK_FONT, text=self.song_name, border=0)
        tk_canvas.create_window(-375, -250, window=self.title)

        # read from the midi file
        song_file = "midi_files\\" + selected_song[0]
        self.notes_data, self.tempo = ReadMidi.readMidi(song_file)

        self.notes_list = []
        self.barlines_list = []
        self.load_notes()
        self.load_barlines()

        self.staff = draw_staff(clef)    

        # piano keyboard for user input
        self.keyboard = Keyboard(self.notes_list)

        # button to show note letters
        self.note_name_button = tk.Button(tk_canvas.master, bg="white", height=1, width=15, font=TK_FONT, text="Show Note Names", border=0, activebackground="CadetBlue3", command=self.show_note_names)
        tk_canvas.create_window(0, -250, window=self.note_name_button)
        
    def load_notes(self):
        """add notes to the list of notes"""
        for pitch_num, note_letter, note_length, absolute_time in self.notes_data: 
            note = Note(pitch_num, note_letter, note_length, absolute_time, self.time_signature, self.key_signature)
            self.notes_list.append(note)
    
    def load_barlines(self): 
        """add barlines to the list of barlines"""
        total_beats = int(self.notes_data[-1][-1] * (self.time_signature[1] / 4))
        for beat in range(total_beats):
            beat += 1 # beats start at 1
            if (beat % self.time_signature[0] == 0): 
                barline = Barline(beat, self.time_signature)
                self.barlines_list.append(barline)
        # double barline
        beat += 1
        barline = Barline(beat, self.time_signature)
        self.barlines_list.append(barline)
        barline = Barline(beat+.1, self.time_signature)
        self.barlines_list.append(barline)

    def show_note_names(self):
        """shows the note names on the turtle screen, pauses all other actions while note names are shown"""
        for note in self.notes_list: 
            note.draw_letter()
        time.sleep(0.5)
        for note in self.notes_list: 
            note.painter.clear()

    def play(self):
        """mainloop for moving the note/barline objects"""
        clock = pygame.time.Clock()
        while (len(self.barlines_list) > 0 or len(self.notes_list) > 0): 
            for note in self.notes_list: 
                note.update()
                if (note.x < -WINDOW_WIDTH/2 + 210): 
                    # delete note if reaches far left
                    note.painter.clear()
                    self.notes_list.remove(note)
                elif (note.x < -WINDOW_WIDTH/2 + 270 and note.is_played == False): 
                    # stop notes from moving if note hasn't been played
                    for note in self.notes_list: 
                        note.move_right()
                    # also stop barlines from moving
                    for barline in self.barlines_list: 
                        barline.move_right()

            for barline in self.barlines_list: 
                barline.update()
                if (barline.x < -WINDOW_WIDTH/2 + 210): 
                    barline.painter.clear()
                    self.barlines_list.remove(barline)
            
            clock.tick(self.tempo)
            window.update()
        
    def clear(self):
        """function to clear all painters and delete the song"""
        # traverse each list to delete all elements
        i = len(self.notes_list) - 1 
        while (i >= 0):
            note = self.notes_list[i]
            note.painter.clear()
            self.notes_list.pop()
            i -= 1
        i = len(self.barlines_list) - 1
        while (i >= 0):
            barline = self.barlines_list[i]
            barline.painter.clear()
            self.barlines_list.pop()
            i -= 1
        self.title.destroy()

class Note():
    """Create notes to display on the window. 
    Notes keep the same y coordinate (based on pitch) and can move left along the window"""

    def __init__(self, pitch_num, note_letter, note_length, absolute_time, time_signature, key_signature): 
        """Initialize note info to variables"""
        self.letter = note_letter
        self.length = note_length
        self.pitch_num = pitch_num
        self.y = get_y(pitch_num, key_signature)
        self.x = get_x(absolute_time-note_length, time_signature, "note")
        self.ledger = True if (pitch_num <= 60 or pitch_num >= 81) else False
        self.painter = create_painter(self.x, self.y)
        self.is_played = False

    def oval(self): 
        """Function for drawing noteheads"""
        self.painter.goto(self.x, self.y) 
        # check if the note should be filled (filled for quarter notes and shorter notes)
        if (self.length < 1.01): 
            self.painter.fillcolor(self.painter.pencolor())
            self.painter.begin_fill()
        # draw the notehead
        self.painter.pendown()
        self.painter.setheading(150)
        self.painter.circle(10*NOTE_SIZE, 90)
        self.painter.circle(4*NOTE_SIZE, 90)
        self.painter.circle(10*NOTE_SIZE, 90)
        self.painter.circle(4*NOTE_SIZE, 90)
        self.painter.penup()
        self.painter.end_fill()
        self.note_stem()

    def note_stem(self): 
        """Function for drawing stems on noteheads"""
        self.painter.goto(self.x + NOTE_SIZE*2, self.y - NOTE_SIZE*2)
        # draw the stem unless note is a whole note (4 beats)
        if (self.length < 3.99): 
            self.painter.pendown()
            self.painter.setheading(90)
            self.painter.forward(40*NOTE_SIZE)
            self.painter.penup()
    
    def ledger_line(self): 
        """Function for drawing ledger lines for notes that go off the staff"""
        self.painter.goto(self.x + NOTE_SIZE*2 + 20, self.y - NOTE_SIZE*2 - 8)
        self.painter.pendown()
        self.painter.setheading(-180)
        self.painter.forward(30*NOTE_SIZE)
        self.painter.penup()

    def draw_letter(self): 
        """Function for drawing the letters for notes"""
        self.painter.goto(self.x + NOTE_SIZE*2 - 25, self.y-80)
        self.painter.color("CadetBlue3")
        self.painter.pendown()
        self.painter.write(self.letter, font=TURTLE_FONT, align='center')
        self.painter.penup()
        self.painter.color("black")

    def move_left(self):
        """Set the new x position to the left"""
        self.x -= 1
    
    def move_right(self): 
        """Set the new x position to the right"""
        self.x += 1

    def update(self): 
        """Updates the position of the object
        Only draws notes if it is on window"""
        self.move_left()
        if (self.x < WINDOW_WIDTH/2 + 50):
            self.painter.clear()
            self.oval()
            self.note_stem()
            # check if ledger lines are necessary
            if (self.ledger): 
                self.ledger_line()

    def play_note(self):
        self.painter.pencolor("green")
        self.is_played = True
        # play the sounds

class Barline():
    """Create notes to display on the window."""
    
    def __init__(self, beat, time_signature):
        self.x = get_x(beat, time_signature, "barline")
        self.y = WINDOW_HEIGHT/2 - NOTE_DISTANCE*15
        self.painter = create_painter(self.x, self.y)

    def draw_barline(self): 
        """Function for drawing barlines"""
        self.painter.goto(self.x, self.y)
        self.painter.pendown()
        self.painter.setheading(90)
        self.painter.forward(NOTE_DISTANCE*8)
        self.painter.penup()

    def move_left(self):
        """Set the new x position to the left"""
        self.x -= 1

    def move_right(self): 
        """Set the new x position to the right"""
        self.x += 1

    def update(self): 
        """Updates the position of the barline
        Only draws barlines if it is on window"""
        self.move_left()
        if (self.x < WINDOW_WIDTH/2 + 50):
            self.painter.clear()
            self.draw_barline()


#############################################################################################################
#   Keyboard 
#############################################################################################################

class Keyboard():
    """Displays a piano keyboard and listens for user input (clicking on a piano key)"""
    def __init__(self, notes_list):
        # create keyboard
        self.keyboard = create_painter(-450,-100)
        self.keyboard.pendown()
        self.keyboard.write("Click keys on the piano to play notes: ", font=('Times', 15))
        self.keyboard.penup()
        self.keyboard.goto(0,-187)
        self.keyboard.showturtle()
        window.addshape(keyboard_pic)
        self.keyboard.shape(keyboard_pic)

        self.notes_list = notes_list
        window.onscreenclick(self.click)

    def click(self, x, y): 
        """Called when user presses on screen. Plays the note chosen on the keyboard"""
        if (y > -250 and y < -115):
            pitch_num = self.get_pitch_num(x,y)
            self.check_correct(pitch_num)

    def get_pitch_num(self, x, y): 
        """Returns the pitch num based on the location that was clicked"""
        # white key
        interval = 2*(x//23 + 3)    # interval from middle C, measured in half-steps
        # black key
        if y > -210: 
            black_keys_x = (-47+162,-25+162,22,44,67) 
            for black_key in black_keys_x:
                if x % 162 >= black_key - 8.5 and x % 162 <= black_key + 8.5:  # checks if a x position is on a black key (x % 162 to keep it in one octave)
                    interval = 2*((x+8.5)//23 + 3) - 1
        octave = interval // 14     # get the octave from middle C
        interval = interval % 14    # get the interval from the start of the octave
        if interval > 4: 
            interval -= 1
        if interval > 11: 
            interval -= 1
        pitch_num = int(60 + interval + (octave*12))
        return pitch_num

    def check_correct(self, pitch_num):
        current_note = self.notes_list[0]
        if pitch_num == current_note.pitch_num: 
            current_note.play_note()


#############################################################################################################
#   Run Program
#############################################################################################################
if __name__ == "__main__":
    song_selection = Song_Selection(window, CSV_FILE)

    window.listen()
    window.mainloop()