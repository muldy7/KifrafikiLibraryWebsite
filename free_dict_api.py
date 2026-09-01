import requests

# function to look up with with the free dictionary api

#links:
# big thanks to these sources and some help from googleAI
#https://dictionaryapi.dev/
#https://freedictionaryapi.com/
#https://freeapihub.com/blog/free-dictionary-api-tutorial-word-lookup-tool

# function to import into my file
def lookup_word(word):
    url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true" # url used for kiswahili
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
            output = "" # init the entry variable
            for entry in data['entries']: # for loop to see each definition 
                part_of_speech = entry['partOfSpeech']

                # 2. Loop through each sense in the 'senses' list
                for sense in entry['senses']:
                    definition = sense['definition']

                    if output != "": # add all the definitions together but skip the first time through 
                        output = output +"; " + definition # can maybe change this to make it look a little better 
                    else: 
                        output = definition
                    # 3. Print out the part of speech and definition
                    #print(f"[{part_of_speech}]: {definition}")

            return output #print the list of definitions 
    except (KeyError, IndexError, ValueError):
        print("Could not parse the response.")
        return None


if __name__ == "__main__":
    lookup_word("asdfghjkl")
    output = lookup_word("happy")
    if output is None:
        print("no definition found")
    output = lookup_word("jambo")
    print(output)