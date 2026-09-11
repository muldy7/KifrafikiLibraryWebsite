# this is for defining the function that will call to the database to look for a dictionary entry
# for now I will just enter the words through the database tool idk

from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone 
from deep_translator import GoogleTranslator, MyMemoryTranslator
import string 
import requests
import re

#from .models import DictionaryEntry

# this will look up a dictionary entry and if it doesn't exist it should call for the API? It can then ask if it wasn't to change it 
# question = get_object_or_404(Question, pk=question_id)

# I think for the view I'll want to have a question that is like "Detected new word, would you like to add to the database?" idk something like that. but this translation tool is free and easy to do 
# so I want to set it up just idk where I'll use it 


# FUNCTION #1 Free API Call
## function to look up with with the free dictionary api
# could add synonym and other things later if I want to

#links:
# big thanks to these sources and some help from googleAI
#https://dictionaryapi.dev/
#https://freedictionaryapi.com/
#https://freeapihub.com/blog/free-dictionary-api-tutorial-word-lookup-tool
# https://docs.python.org/3/library/re.html

# function to import into my file
# function to just get a definition since some can be annoying if they are infinitives or plurals but will need more testing

def simple_lookup(word):
    url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true" # url used for kiswahili
    try:
        response = requests.get(url, timeout=5) # try and skip if its taking too long
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        definition = "N/A"
        return definition

    if response.status_code == 404:
        print(f"Sorry, '{word}' was not found.")
        definition = "N/A"
        return definition

    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        definition = "N/A"
        return definition

    # main meaning grabbed from the url requests
    try:
        data = response.json()
        print(data)
        if not data['entries']: # if nothing is found in entires we'll continue and output none
            print(f"No definitions found for the word '{data['word']}'.")
            definition = "N/A"
            return definition
        else: # if there is an entry
            def_output = "" # init the entry variable for the definition output
           
            for entry in data['entries']: # for loop to see each definition 
                for sense in entry['senses']:
                    definition = sense['definition']

                    if def_output != "": # add all the definitions together but skip the first time through 
                        def_output = def_output +"; " + definition # can maybe change this to make it look a little better 
                    else: 
                        def_output = definition
                    # 3. Print out the part of speech and definition
                    #print(f"[{part_of_speech}]: {definition}")

            return def_output
        
    except (KeyError, IndexError, ValueError):
        print("Could not parse the response.")
        return None

# main look up function to be used with my translate funciton 
def lookup_word(word):
    # thank you chatgpt for this regex pattern to elimate the silly stuff from the api call
    # Regex breakdown:
    pattern = r'\[\[[^]#]+#(.*?)\|.*?\]\]'

    # api call URL
    url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true" # url used for kiswahili
    #print(url)
    try:
        response = requests.get(url, timeout=5) # try and skip if its taking too long
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

    if response.status_code == 404:
        print(f"Sorry, '{word}' was not found.")
        return None

    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        return None

    # main meaning grabbed from the url requests
    try:
        data = response.json()
        print(data)
        if not data['entries']: # if nothing is found in entires we'll continue and output none
            print(f"No definitions found for the word '{data['word']}'.")
            return None
        else: # if there is an entry
            def_output = "" # init the entry variable for the definition output
            pof_output = "" # variable for part of speech, starting as empty string 
            example_output = "" # variable for grabbing examples 

            # con output variable this is the default value if nothing is changed
            con_output = "No construction found" # think i like this better but could also be empty string """

            # going to set a change flag to change it at the end I think that will be easier
            con_flag = 0

            for entry in data['entries']: # for loop to see each definition 
                # loud the part of speech
                part_of_speech = entry['partOfSpeech']

                if pof_output != "": # add all the definitions together but skip the first time through 
                    if part_of_speech != pof_output: # also make sure it's just not the same thing twice
                        pof_output = pof_output +"; " + part_of_speech # can maybe change this to make it look a little better 
                else: 
                    pof_output = part_of_speech

                # 2. Loop through each sense in the 'senses' list
                # okay these definitions are annoying if they are plural or infinitives so we need to change that
                # it should test to see if it contains 'plural' or 'infinitive' and then get that definition
                # I can make a 'simple_lookup' to just get the definition and then add it
                # let's try it 
                for sense in entry['senses']:
                    # definition and example look-up here 
                    definition = sense['definition']
                    example = sense['examples']
                    
                    ## LOTS OF FIXES HERE 
                    # let's fix the annoyin 'infitive of' definitions I can get
                    # I could also add a bit about construction but that makes it over complicated I feel like 
                    # look for infinitive first before looking for other annoying verbs 
                    if 'infinitive' in definition:
                        # extract the word following the hyphen
                        match = re.search(r'-(\w+)', definition) # works similar to regex in excel
                        
                        if match:
                            extracted_word = match.group(1) # group(0) stores the trigger word and we dont want that
                            inf_def = simple_lookup(extracted_word) # do a simple lookup for the extracted verb
                            con_output = definition + " (" + inf_def + ")" # should add the new definition in parenthesis
                            # con_output = definition # put the definition in construction instead 
                            definition = inf_def # set the definition as the infinitive definition 

                    # see if there's some weird verb stuff going on like "sipendi" or "anataka"
                    elif '-' in definition:
                        con_flag = 1 # just going to call the flag to put definition in construction and ask for a translation since it might get messed up
                    

                    # this time check if 'plural' is in the definition since its really useless if that's all we get
                    elif 'plural' in definition:
                        # this time just grab the last word in the string
                        extracted_word = definition.split()[-1]
                                            
                        plural_def = simple_lookup(extracted_word) # do a simple lookup for the extracted verb
                        definition = definition + " (" + plural_def + ")" # should add the new definition in parenthesis
                        #definition = "None" # need to do a Google API call to get the definiton
                        # set the construction flag to 1 
                        con_flag = 1
                    else:
                        pass # not sure if i need to do this but just to be safe 

                    # also need to eliminate 'inflected' and the silly appendix stuff and this is done no matter what 
                    # inflected is also a dumb word so maybe we can change that with something else it would be helpful
                    # so these inflected ones are annoying, can talk to people and see if that stuff would better fit in "constructions" and then could use a simple english translation
                    if 'Appendix' in definition:
                        clean_text = re.sub(pattern, r'\1', definition) # using the pattern above look for the value inbetween # and |
                        if 'inflected' in clean_text:
                            match = re.search(r'-(\w+)$', clean_text) # works similar to regex in excel, want to make sure its at the end of the string with $
                        
                            if match:
                                extracted_word = match.group(1) # group(0) stores the trigger word and we dont want that

                                # it doesn't like 'a' for whatever reason so we'll add that manually
                                if extracted_word == 'a':
                                    inflected_def = 'of' # this makes it super easy 
                                else:
                                    inflected_def = simple_lookup(extracted_word) # do a simple lookup for the extracted verb
                                definition = clean_text + " (" + inflected_def + ")" # should add the new definition in parenthesis

                                # could do this for ornative too because that is a dumb word
                                # could probably get rid of the parenthesis but I'll leave that for now 
                                definition = definition.replace('inflected','modified (inflected)') # inflected is a dumb word so we're going to replace it
                                definition = definition.replace('ornative','"thing having" (ornative)') # ornative is a dumb word so we're going to replace it
                                #definition = "None" # tell the translate function we need a new definition
                                # set the construction flag to 1 
                                con_flag = 1

                                # could probably take out this google translate addition but feel like it might be helpful
                                # like the vibe of this since it actually brings a word but can change it later 
                                #google_addition = GoogleTranslator(source='swahili', target='english').translate(word) # going to see if we can help out the entry with google?
                                #definition = google_addition + " [" + definition + "]"

                            else:
                                definition = clean_text # just output the clean text if we can't find anything 
                        else:
                            definition = clean_text # don't need to do anything if there's no inflected we'll just keep it as the clean text

                    # add the definitions together 
                    if def_output != "": # add all the definitions together but skip the first time through 
                        def_output = def_output + "; " + definition # can maybe change this to make it look a little better 
                    else: 
                        def_output = definition

                    # add the examples together just like definitions

                    if example_output != "" and example_output != []: # add all the definitions together but skip the first time through 
                        example_output = example_output + example # add multiple lists together if they're there 
                    else: 
                        example_output = example

            # check flag before outputitng
            if con_flag == 1:
                # if the flag has been flipped we need to switch the stuff 
                con_output = definition
                def_output = None

            # if it's just an empty list we don't want that
            # but we want to convert the examples to a string at the end 
            if example_output == []:
                example_output = "No examples found"

            return def_output, pof_output, con_output, example_output #print the list of definitions and part of speech, can maybe organize this better but okay for now
        
    except (KeyError, IndexError, ValueError) as e:
       print("Could not parse the response.")
       print(e)
       return None



# FUNCTION #2: translate word in database, if I want to use it later I'll have it but otherwise I can just get from the database

# something to do with proper nouns
# or honestly maybe I can add stuff to the database. Then, people can click on a word and if it has no definition they can press a button
# and translate it, then add the stuff to the database. That sounds like the best way to do it! Then it can populate stuff from the 
# free dict if I get the chance. 
# think best thing to do is if this changes something in the view so it's a pop-up if it's not already in the database? 
# this will come way later I think, so next would be a helpful tool for uploading stories and manually entering them. 
# but i can have it so I can press the translate button and then fill some fields that would be awesome.

# TO-DO
# 1. the free dictionary pulls stuff that's there so it can populate the fields
# 2. I can ignore proper nouns since they would just be bothersome 
# 3. new words can be submitted automatically and then later we'll have a buffer or something like that 
# 4. story entering tool
# 5. buffer for words that aren't added but have been translated
# 6. timeout for the APIs

# HELPFUL LINKS
# python dictionaries: https://www.w3schools.com/python/python_dictionaries.asp

# text needs to be input as clean text
def simple_translate(text):
    try:
        # Use translation fallback to GoogleTranslate
        definition = GoogleTranslator(source='sw', target='en').translate(text)
        #source = "GoogleAPI" 
        
      
    except Exception as e:
        print(f"Error during API translation/saving: {e}")
                    
        try:
            print("trying again") # my memory translator really sucks so I'll get an API figured out for DeepL, can use something else here in case google fails
            definition = GoogleTranslator(source='sw', target='en').translate(text)
            #source = "GoogleAPI"    # not sure if this is the best way to do it but we'll see, doing a lot of work then can ask for help. 
    
        except Exception as e:
            print(f"Error during API translation/saving: {e}")
            try:
                print("trying again with my memory translator") # my memory translator really sucks so I'll get an API figured out for DeepL, can use something else here in case google fails
                definition = MyMemoryTranslator(source='swahili', target='english').translate(text)
                #source = "GoogleAPI"    # not sure if this is the best way to do it but we'll see, doing a lot of work then can ask for help. 
                
            except Exception as e:
                print(f"Error during API translation/saving: {e}")
                definition = "No Definition Found" 
             

    return definition

# give a list of examples so it can translate each one into a long string
def example_translate(list):
    examples = ""
    # for loop to add all the examples from the list in
    for example in list:
        if examples != "":
            examples = examples + '; ' + example + ' = ' + simple_translate(example) # make a longer list
        else:
            examples = example + ' = ' + simple_translate(example) # translate the example and add it to the list

    return examples 

def translate_word(text):
    # big ups to google AI for this helpful bit
    # Standardise text: remove punctuation and make lowercase
    #clean_text = text.replace('\r\n', ' ').replace('\n', ' ')   # remove any time enter has been pressed
    #if text == '\n':
    #    return ""

    # initial variables so not to mess up stuff later
    source = "No source found"
    part_of_speech = "No part of speech found"
    construction = "No construction found" # added for construction stuff oof, init so its empty at first
    example = 'No examples found'
 
    clean_text = text.strip(string.punctuation).lower() # need to make sure this doesn't mess up ng'ombe
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

    api_call = lookup_word(clean_text) # see if it's in the api call, plus will grab the part of speech from the api

    # see if there's nothing in the api call result 
    if api_call is None: 
        # use simple translate to get text from the api
        definition = simple_translate(clean_text)
        source = "GoogleTranslate" 

    # see if there's only no definition from the api call 
    elif api_call[0] is None: # could probably put this google api in a seperate function since i'm doing it twice, 
        # get the definition but just the definiton from google translate
        definition = simple_translate(clean_text)

        # get the other things from the Free Dictionary API
        part_of_speech = api_call[1] 
        construction = api_call[2]
        example_list = api_call[3] # get the list if its there
        if "No" in example_list: # check to see if the list is just a string
            pass
        else:
            example = example_translate(example_list) # give the list to the example translate function 
        source = f'https://en.wiktionary.org/wiki/{clean_text}#Swahili'
        

    # if there is a definition and there is an api call
    else:
        print("definition found on FreeDictionaryAPI") # wow! good work Abe that was awesome, I really like those definitions so maybe I add them or just use those? idk
        definition = api_call[0] # get the definition and the part of speech from the function since its stored in a tuple, if there's a defintion 
        part_of_speech = api_call[1] 
        construction = api_call[2]
        example_list = api_call[3] # get the list if its there
        if "No" in example_list: # check to see if the list is just a string
            pass
        else:
            example = example_translate(example_list) # give the list to the example translate function 
        source = f'https://en.wiktionary.org/wiki/{clean_text}#Swahili' # this should then tell the view that this is the source, I could also grab the actual link but that's a lot of work 

    # make a dictionary entry that can be used later by views 
    # this will be output with a kiswahili word, definition in english, part of speech, and a source, can add sources later if i want, and date added
    # matching how I wrote them in my models
    # could add construction here later if that's helpful and maybe noun class? also examples
    new_entry = {
        "swahili_entry": clean_text,
        "english": definition,
        "part_of_speech": part_of_speech,
        'construction': construction,
        #"date_added": timezone.now(), # i could also do this on the views side but might as well get it done now, not going to work since this isn't in django
        'sentence': example,
        'translation_source': source
    }

    return new_entry # output as a dictionary field 


if __name__ == "__main__":

    # testing code for lookup_word with free api call
    # lookup_word("asdfghjkl")
    # output = lookup_word("happy")
    # if output is None:
    #     print("no definition found")
    # output = lookup_word("jambo")
    # print(output)

    # test the translate word function
    # new_entry = translate_word("mbuzi") # mbuzi should only output one part of speech even though it has different definitions
    #new_entry = translate_word("ng'ombe") # ng'ombe works fine with the apostrephe this entry has a lot of examples too 
    new_entry = translate_word("sitaki")
    print(new_entry)
    print(new_entry["swahili_entry"])
    example = new_entry['sentence']
    print(example)

    # try sitaki and anataka
    # okay awesome that worked great

    #word = simple_translate(example)
    #print(word)


    # TESTING NOTES
    # infinitive works!
    # okay I think best thing to do is to do a flag at the end that says "hey switch construction to definition"
    # there might be cases where it doesn't work but i feel like that's okay
    # problem if there are multiple inflected definitions
    # okay I feel like that is working good, and that's why this will be crowd sourced we will have to add definitons!
    # okay the examples are kinda useless since they don't have a translation but I'm scared about adding that 
    # going to add the link instead of worring about the translation of examples so its easy to go and look at that
    # added the link since I think that's nice and will be cool to have a bunch of different links to stuff