# Read the Midi Files

# pip install mido==1.2.9
import mido
from mido import MidiFile, MetaMessage


def readMidi(filename): 
    """Returns a list of note data, time signature, and tempo of a given filename"""
    mid = MidiFile(filename, clip=True)

    # extract information from the midi file
    tempo = get_tempo(mid)

    # get lists of notes (pitch, length)
    notes_data = get_notes(mid, tempo)

    return notes_data, tempo

def get_time_signature(midObj): 
    """Returns the time signature as a tuple: (numerator, denominator)"""
    for track in midObj.tracks: 
        for msg in track:
            if msg.type == "time_signature": 
                # parse through the string for the numerator and denominator
                msg = str(msg)
                numerator = int(msg[msg.index("numerator=") + len("numerator="): msg.index(" denominator")])
                denominator = int(msg[msg.index("denominator=") + len("denominator="): msg.index(" clocks_per_click")])
                return (numerator, denominator)
    # return a 4/4 time signature if none specified
    return (4,4)

def get_tempo(midObj): 
    """Returns the tempo converted to bpm"""
    for track in midObj.tracks: 
        for msg in track:
            msg = str(msg)
            if "tempo" in msg: 
                # parse through the string for the tempo
                tempo = int(msg[msg.index("tempo=") + len("tempo="):msg.index(" time=")])
                return int(mido.tempo2bpm(tempo))
    # return a default of 120 bpm if tempo not specified
    return 120

def get_notes(midObj, tempo): 
    """Returns a list of tuples: (midi number, note pitch, note length in beats) based on data from the input"""
    notes_list = []
    absolute_time = 0
    for msg in midObj: 
        # based on note releases
        if "note_off" in str(msg): 
            midi_num = msg.note
            note_pitch = get_pitch(midi_num) # convert midi note number to letter form
            note_length = (msg.time*tempo/60) # rounding
            absolute_time += note_length
            notes_list.append((midi_num, note_pitch, note_length, absolute_time))
    return notes_list

def get_pitch(midi_num): 
    """Returns the note letter of a given midi number"""
    PITCHES = ['C', 'C#/D♭', 'D', 'D#/E♭', 'E', 'F', 'F#/G♭', 'G', 'G#/A♭', 'A', 'A#/B♭', 'B']
    pitch = PITCHES[midi_num % 12]
    return pitch

if __name__ == "__main__": 
    MUSICFILE = "Amazing_Grace.mid"
    notes, time_signature, tempo = readMidi(MUSICFILE)
    print(notes)
    print("Time Signature: " + str(time_signature[0]) + "/" + str(time_signature[1]))
    print("Tempo (BPM): " + str(tempo))


# figure out how to deal with a pickup