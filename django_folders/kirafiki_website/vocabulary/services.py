import random
import genanki

# css file from claude
def make_model():
    """
    This is a simple function to create a model for an anki deck 

    """
    # css file to be used with the deck that can be update

    css = """
    /* ==========================================================================
    Kiswahili Vocabulary — Anki Card Styling
    this is just a filler css from Claude
    Clean, minimal layout using the colors of the East African Community
    flag: Lake Victoria blue, gold, green, black and red on a soft white
    background. Works in both light mode and Anki's night mode.
    ========================================================================== */

    :root {
    --bg: #F7F6F2;
    --text: #1F1F1F;
    --muted: #5C5C5C;
    --blue: #1B3A6B;   /* Lake Victoria blue */
    --gold: #E6B319;   /* EAC yellow stripe */
    --green: #1E7145;  /* EAC green */
    --red: #B23A2E;    /* EAC red */
    --card-border: #E1DED6;
    }

    .night_mode {
    --bg: #1C1E22;
    --text: #F1EFE9;
    --muted: #e6e3dc;
    --blue: #6E93C9;
    --gold: #F0CB56;
    --green: #4FA579;
    --red: #E0796A;
    --card-border: #33363B;
    }

    .card {
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    text-align: center;
    padding: 40px 24px;
    max-width: 480px;
    margin: 0 auto;
    }

    /* The Swahili word itself — the visual centerpiece */
    .word {
    font-size: 2.1em;
    font-weight: 700;
    color: var(--blue);
    letter-spacing: 0.01em;
    margin-bottom: 6px;
    }

    /* Small label under/above the word, e.g. part of speech */
    .tag {
    display: inline-block;
    font-size: 0.72em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--green);
    margin-bottom: 14px;
    }

    /* Thin divider between front/back sections, accented with the gold stripe */
    hr, .divider {
    border: none;
    height: 2px;
    background: var(--green);
    margin: 22px auto;
    width: 60%;
    border-radius: 2px;
    }

    /* English meaning */
    .meaning {
    font-size: 1.3em;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 18px;
    }

    /* Example sentence, set apart in a subtle bordered block */
    .example {
    font-size: 0.95em;
    font-style: italic;
    color: var(--muted);
    background: #498ec9;
    border-left: 3px solid var(--green);
    padding: 10px 16px;
    text-align: left;
    border-radius: 4px;
    margin: 0 auto;
    max-width: 90%;
    line-height: 1.5;
    }

    /* Optional: highlight the vocab word if it also appears inside the example */
    .example b, .example strong {
    color: var(--red);
    font-style: normal;
    }
    """

    # make the model using the css file, right now we'll have swahili on the from then the english and example on the back
    my_model = genanki.Model(1607392319, 'Simple Model', fields=[{'name': 'Swahili Word'},{'name':'Meaning'},{'name': 'Example'},], 
                             templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div class="word">{{Swahili Word}}',
            'afmt': '''{{FrontSide}}<hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="example">{{Example}}</div>''',
            },
        ],
    css= css
    )

    return my_model 

# okay I can have this be fancy but for now I'll stick to the basics 
# the basic unit of anki is a 'note'
# this notes can correspond to one or more cards

def create_note(model,swahili,english,example):
    """
    Function to create a basic note for the deck
    """
    my_note = genanki.Note(model=model, fields=[swahili,english,example])

    return my_note


def create_deck(notes):
    """
    Make a deck from a list of notes given to the function, creates a random number for each deck
    """
    random_id = random.randrange(1 << 30, 1 << 31)

    my_deck = genanki.Deck(
        random_id,
        'Kirafiki Vocabulary')

    for note in notes:
        my_deck.add_note(note)

    return my_deck

# you put in a model and gets fields which can be HTML

# a model defines the fields and cards for a type of Note. 

# this can also take a custom css if I want to do that 

# test code
if __name__ == "__main__":
    # generating a Anki deck, each deck should get a custom deck_id, so I can do that for every person I guess
    my_note = create_note('mbwa','test','test')
    
    my_deck = genanki.Deck(
    2059400110,
    'Kirafiki Vocabulary')

    my_deck.add_note(my_note)

    genanki.Package(my_deck).write_to_file('output_test.apkg')