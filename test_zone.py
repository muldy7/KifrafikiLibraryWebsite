# # ## test_zone

# # from pymongo import MongoClient

# # # Connect to MongoDB client
# # client = MongoClient("mongodb+srv://abe_db_user:BYgiV2Ysm8oK9y5u@kirafikicluster.k0x7uss.mongodb.net/") # connect to online database
# # db = client["dictionary"]   # load the specific database
# # collection = db["sw_en"]    # load the collection in the database

# # definition = collection.find_one({"WORD": "miaka"}) # can look for word in the collection 

# # print(definition) # print the full entry
# # print(definition["DEFINITION"])    # print just the meaning 

# # # adding a definition to MondoDB
# # # User-modified Python dictionary
# # user_dict = {'WORD': 'test','DEFINITION': 'test complete'} # user id will be completed automatically 

# # # Insert into MongoDB
# # collection.insert_one(user_dict)

# # # test to use if it made it to the database
# # test = collection.find_one({"WORD": 'test'})
# # print(test)

# # #update test
# # # can use object_id just to be sure
# # #collection.update_one({'WORD': 'test'}, {"$set": {"DEFINITION": 'update test complete'}}) # this makes a new entry

# # collection.replace_one({'WORD': 'test'}, {'WORD': 'test',"DEFINITION": 'update test complete'}) # want to use replace_one instead

# # # think the best think to do is to use the object id so not to get stuff mixed up

# word = 10

# try:
#     int(word)
#     print(word)
# except ValueError:
#     print("not a number")

## free dictionary api call

# def lookup_word(word):
#     # Construct the API URL for the target word
#     url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true"
#     print(url)https://api.dictionaryapi.dev/api/v2/entries/en/{word}

#     try:
#         # Make the network request
#         with urllib.request.urlopen(url) as response:
#             data = json.loads(response.read().decode())
            
#             # Parse and display the data
#             print(f"Word: {data[0]['word']}")
#             print(f"Phonetic: {data[0].get('phonetic', 'N/A')}\n")
            
#             for meaning in data[0]['meanings']:
#                 print(f"[{meaning['partOfSpeech']}]")
#                 for definition in meaning['definitions']:
#                     print(f" - {definition['definition']}")
                    
#     except Exception as e:
#         print(f"Could not find definitions for '{word}'. Details: {e}")

# # Example execution
# lookup_word('jambo')

# import requests

# def lookup_word(word):
#     url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true"
#     print(url)
#     response = requests.get(url)
#     data = response.json()
#     print(data)

#     if data['entries'] == None:
#         print("no definition found")
#     # 1. Loop through each entry in the 'entries' list
#     for entry in data['entries']:
#         part_of_speech = entry['partOfSpeech']

        
#         # 2. Loop through each sense in the 'senses' list
#         for sense in entry['senses']:
#             definition = sense['definition']

#             if output != "":
#                 output = output +"; " + definition # can maybe change this to make it look a little better 
#             else: 
#                 output = definition
#             # 3. Print out the part of speech and definition
#             print(f"[{part_of_speech}]: {definition}")

#     return output 

# defintion = lookup_word("aliyeanguka")
# print(defintion)

# if defintion == None:
#     print("no definition found")
import requests

def lookup_word(word):
    url = f"https://freedictionaryapi.com/api/v1/entries/sw/{word}?translations=true"
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

    if response.status_code == 404:
        print(f"Sorry, '{word}' was not found.")
        return None

    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        return None

    try:
        data = response.json()
        print(data)
        if not data['entries']:
            print(f"No definitions found for the word '{data['word']}'.")
            return None
        else:
            output = ""
            for entry in data['entries']:
                part_of_speech = entry['partOfSpeech']

            
                # 2. Loop through each sense in the 'senses' list
                for sense in entry['senses']:
                    definition = sense['definition']

                    if output != "":
                        output = output +"; " + definition # can maybe change this to make it look a little better 
                    else: 
                        output = definition
                    # 3. Print out the part of speech and definition
                    print(f"[{part_of_speech}]: {definition}")

            return output 
    except (KeyError, IndexError, ValueError):
        print("Could not parse the response.")
        return None


if __name__ == "__main__":
    lookup_word("asdfghjkl")
    output = lookup_word("happy")
    if output == None:
        print("no definition found")
    output = lookup_word("jambo")
    print(output)