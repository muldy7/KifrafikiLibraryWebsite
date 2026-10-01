# Import necessary libraries
from deep_translator import GoogleTranslator, MyMemoryTranslator
import gradio as gr
import pandas as pd
import string 
from pymongo import MongoClient
from free_dict_api import lookup_word
from pymongo.errors import NetworkTimeout
#from openpyxl import load_workbook as ld_book

# MongoDB User information
# user name
# abe_db_user

# password
# BYgiV2Ysm8oK9y5u

# Connect to MongoDB client
client = MongoClient(MONGO_API_KEY, timeoutMS = 2000) # connect to online database, with timeout
db_dict = client["dictionary"]   # load the specific database

# load the swahili to english collection
en_collection = db_dict["sw_en"]    # load the collection in the database

#dict_en = dict(zip(den[0].astype(str).str.lower(), den[1]))

# okay I'm finding that the translation takes a second so it's probably best if each word gets turnd into a button and then if they
# click on the word it does something. Then it can get it translated instead of having to go through and translate every word. 
# trying to see if batch translate works a little better, I need to remember to do this in a testing zone in case I mess anything up
# I want to see if I can have a native dictionary so I don't have to do all of these every time. 
# okay the batch didn't work I'm going to see if I can change it so its a button to save on a lot of processing power
# seems like there are some cool as LLMs for translation that I can do locally so lets try that first and then I can do a google LPI call?
# just needs more testing and learning and it should be fun
# okay this whole faster translate thing is confusing I'll watch a video later but I bet that would help
# okay batch didn't help at all good try
# fun to think I'll be around kiswahili for another year so I don't need to figure this out all rn
# okay I think the model stufff is SUPER complicated I think it would be best to just see if I can find a free dictionary
# I think the API calls and stuff make it complicated so lets see if the dictionary helps yeah! the button thing is hard 
# and I want to get to a stopping place
# okay I think Im way to tired for this now and the dictionary is just to kiswahili haha
# I could have it add files to the excel file so it doesnt need to do it over and over and over again
# but could have a crowdsourced thing where the definitions are added that would be super cool
# also need to know to look for ku- and maybe if parts of the verb are there? The kiswahili defintions are also hella ngumu
# case sensitive is also messing me up
# I'll have it add to the dictionary to help things out
# I like the idea of having the vocab list that gets added it. It could have the Kiswahili and english definitions and then as people 
# use it then they could add to it. I feel like the kiswahili definitions only are tough to understand for people learning especially
# since they don't always use words that are known
# okay good work abe this was hella fun let me get some sleep now. I like if the website would have some preloaded readings, vocab list,
# then a place where people could upload there own stuff. 
# if I just did custom stories then that would be okay since it would be pre loaded, the uploading seems like a lot of work but ut would be 
# very very cool. SO pole pole and this project is has no time limit since I'll be in Kiswahili ville for a while! Fun to have cool
#side projects to work on and I'm learning a whole lot of new stuff! 
# changing the hex colors looks SICK
# also like how stuff is getting added to the .csv and then I can change the translations but I bet there could be a better system in the future
# the kiswahili definitions are hard but I like them, maybe those could be the default then click for english and add to vocab? idk
# i can get input on that. 
# whatever Claude did sort of worked, I think the kiswahili definitions are just confusing but I'll ask people. Then can figured out
# best way to do a add to vocab list thing and change the dictionary definition so I can crowd source it which would be SUPER cool
# but good work it looks awesome so I'm going to take a break.
# okay this is really awesome. I think it would be okay to just have all the words in one database. And then you could chnage if the kiswahili 
# definition is bad or add english translation. but sometimes the kiswahili definitionsa re good to use your brain a bit.
# I can just connect it to a huge google sheets which I think would be awesome. Then it would slowly build idk. If it has a lot of 
# outreach I can ask for help for upgrading it later.
# can look for a flash cards thing and translate that to excel and use that
# going to stick with the csv file for now since I don't think google sheets is a final solution
# google is kinda freaking out but if the MyMemory sucks too much I can get a free DeepL API key
# also realizing it may be way esier to just make the website that has a couple stories and then I can figure out the translator later
# I have no idea why there's a big ass space but it's okay since I have to go do this okay with django. I also think I like the click and bring up 
# the side bar better, but maybe I can have some harder words with a kiswahili definition or english meaning. soething like that. 

## MONGO_DB
# seems like this will be helpful becuase I can use compass to edit and it's probably way too powerful for what I need but hey I'm learning something
# then I could have a database for user vocab lists and stuff like that
# probably need one for user accounts too I don't know how that works
# 512 mb is not that much so we'll see if I can make it work
# since using the online database might be annoying I can just make sure that I use the excel for testing so I'm not blasting through the wifi
# only lets certain IP address so I can just change then once I have it as a website
# can also host the database locally for when I am doing testing
# fully works with mongodb now and honestly not that slow the issue is just the translation takes some time. I could change it so it
# bulk translates it but I don't think that's helpful becuase they the match would be a little difficult
# I could add a export to excel feature for the vocab list which would be super cool
#excel will definitely be better for testing since it's hosted locally

# free dictionary api
# realizing that omg I can just use the damn dictionary api for kiswahili since I'm going word by word and if that doesn't work go to google 
# translate. I can 1,000 request which is a butt ton and that should take care of a whole lot of words which is awesome

## WORK LOG
#1. add google sheet functionality to add the words there (need a better data base I think)
    # sounds like Mongo DB Atlas would be good 
#2. change some of the definitions so maybe it's the ismple kiswahili ones? can test if it can show both
#2.5. add deepL as the second lanaguage translation source and if it runs out I'll just make a new account
#2.75 want to try and not translate integers or proper nouns but not much I can do. could have it try and int and if it's successful just skip
#3. add the pop up to the right side of the screen and button functionality
#4. add ability to add to dictionary and change definitions
#5. ability to sign in and store vocabular list
#6. think I should try building the website with django, then I can add a couple stories and articles with everything and the pop-ups and what not
#   then I can try and see if I can build the vocab list and the clickable links. Then once all that is working I can do the translator.
#   but a couple stories and a vocab list will keep me damn entertained and I can't figure out the pop-up now since I'm guessing it will be different
#   I should also lean how the freak CSS and HTML works

def add_mongodb(word,definition):
    # create a new entry
    new_entry = {'WORD': word,'DEFINITION': definition} # user id will be completed automatically 

    # insert into mongodb
    try:    # skip if there's a timeout error
        en_collection.insert_one(new_entry)
    except NetworkTimeout:
        print("Can't add to MongoDB")

    return 

def translate(text):
    # big ups to google AI for this helpful bit
    # Standardise text: remove punctuation and make lowercase
    #clean_text = text.replace('\r\n', ' ').replace('\n', ' ')   # remove any time enter has been pressed
    #if text == '\n':
    #    return ""
 

    clean_text = text.strip(string.punctuation).lower()
    #print(clean_text)
    
    if not clean_text:
        return ""

    # limit the amount of translation by skipping numbers
    try:
        int(text)
        print("skipping number")
        return clean_text # should just return the number we got
    except ValueError: # will have a value error if it's not a word
        pass # don't need to do anything 

    # Look up in Swahili dictionary first
    #definition = dict_en.get(clean_text) 

    print("checking MondoDB") # have to remember to add IP Addresss
    # use MongoDB to find in swahili to engish collection
    try:
        doc = en_collection.find_one({"WORD": clean_text})  #find the document in the database with a timeout
    except NetworkTimeout:
        doc = None
    #doc = None # use if MongoDB is being difficult
    #print(doc)
    
    if doc is None: # will output if None not found in MongoDB
        # try the free dictionary API next
        print("word not found in MongoDB, trying Free Dictionary API")
        definition = lookup_word(text)

        if definition is None:
            try:
                # Use translation fallback to GoogleTranslate
                definition = GoogleTranslator(source='sw', target='en').translate(clean_text)
                
                # Update local dictionary variable
                #dict_en[clean_text] = definition

                # add a definition to MondoDB
                add_mongodb(text, definition)

                # FIX: Correctly structure dictionary to save as a 2-column CSV not used for MongoDB
                #df = pd.DataFrame(list(dict_en.items()))
                #df.to_csv(csv_en_path, index=False, header=False)        
                print(f"Saved new translation for: {clean_text}")
            except Exception as e:
                print(f"Error during API translation/saving: {e}")
                
                try:
                    print("trying again") # my memory translator really sucks so I'll get an API figured out for DeepL
                    definition = GoogleTranslator(source='swahili', target='english').translate(clean_text)

                    #add new definition
                    add_mongodb(text, definition)

                except Exception as e:
                    print(f"Error during API translation/saving: {e}")
                    definition = "No Definition Found" 
        else:
            print("definition found on FreeDictionaryAPI") # wow! good work Abe that was awesome, I really like those definitions so maybe I add them or just use those? idk
    else:
        print("definition found in MongoDB")
        definition = doc["DEFINITION"] # grab definition from MongoDB if it's there and doc isnt NONE
        #print(definition)   

    return definition

def generate_hoverable_text(input_text):
    """Parses text and wraps matched words in a custom tooltip HTML structure."""
    words = input_text.split()
    html_output = []

    #translated = MyMemoryTranslator('swahili','english').translate_batch(words) # batch doesnt work
    # oops! time to go to bed I had a zip there haha, trust myself when its a new issue
    for word in words:
        #clean_text = word.strip(string.punctuation)
        definition = translate(word)
        word_url = f"https://en.wiktionary.org/wiki/{word}#Swahili"

        # add a clickable link to the text 
        link_html = (
            f'<div class="tooltip-wrapper">'
            f'  <a href="{word_url}" target="_blank" class="clickable-text-word">{word}</a>'
            f'  <span class="tooltip-box">{definition}</span>'
            f'</div>'
        )
        
        html_output.append(link_html)

        # Wrap the word in a span with custom tooltip attributes to add the hover for html
        #hover_html = f'<span class="tooltip-target" data-tooltip="{definition}">{word}</span>'
        #html_output.append(hover_html)
        
    return " ".join(html_output)


# 2. Add custom CSS for a beautiful popup design
# thanks AI this is helpful for changing the design 
#removed the underline
# this is the style sheet for what I'm looking at 
#text-decoration: underline dashed #3122ff;
# this CSS stuff I don't super understand but I can find good documentation on it

custom_css = """
.tooltip-container {
    font-size: 16px;
    line-height: 1.6; //
}
.tooltip-target {
    
    color: #00A3DD; 
    cursor: default;
    position: relative;
    display: inline-block;
}
/* Wrapper container for each word */
.tooltip-wrapper {
    position: relative;
    display: inline-block;
    margin-right: 0px; /* Space between words */
}

/* The clickable word link */
.clickable-text-word {
    color: #00A3DD; 
    text-decoration: none;
    cursor: pointer;
    display: inline-block;
    transition: color 0.2s ease;
}

.clickable-text-word:hover {
    color: #01596b; /* Translated text hover color */
}

/* Tooltip popup box styling */
.tooltip-box {
    visibility: hidden;
    width: 100px;
    background-color: #333;
    color: #fff;
    text-align: left;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    line-height: 1.4;
    white-space: normal;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    
    /* Position directly above the word */
    position: absolute;
    bottom: 125%; 
    left: 50%;
    transform: translateX(-50%);
    
    /* Forces Gradio to render it on top of other words/rows */
    z-index: 99999 !important; 
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease-in-out, visibility 0.2s;
}

/* Show tooltip when hovering anywhere over the word wrapper */
.tooltip-wrapper:hover .tooltip-box {
    visibility: visible;
    opacity: 1;
}

/* Your button styles */
#green_btn {
    background-color: #1EB53A !important;
    color: white !important;
}
#green_btn:hover {
    background-color: #1b9e33 !important;
}
"""

# 3. Build the Gradio App
with gr.Blocks() as demo:
    gr.Markdown("### kiRafiki")
    gr.Markdown("Your Kiswahili reading buddy! Write any Kiswahili text and each word will be given a pop-up translation")
    
    user_input = gr.Textbox(
        label="Enter Text", 
        value="Andika Kiswahili hapa"
    )
    
    # Target HTML output block
    output_html = gr.HTML(label="Interactive Output", elem_classes="tooltip-container")
    
    # Trigger transformation automatically on input or submit button
    generate_button= gr.Button("Translate Text",elem_id="green_btn")
    generate_button.click(fn=generate_hoverable_text, inputs=user_input, outputs=output_html)
    
    # Load initial default text representation on page startup
    #demo.load(fn=generate_hoverable_text, inputs=user_input, outputs=output_html)

demo.launch(css=custom_css)
