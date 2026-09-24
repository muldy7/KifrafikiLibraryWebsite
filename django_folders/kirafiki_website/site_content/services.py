# FOR TESTING SITE_CONTENT READER VIEW


if __name__ == "__main__":
    # test code
    content_body = "Hello this \n is a$test \n\n" \
                    "to see if \n this is working"
    paragraphs = content_body.split('\n\n')
    
    structured_content = []
    for para in paragraphs:
        # split each paragraph into lines by single newlines
        lines = para.split('\n')
        para_lines = []
        for line in lines:
            # split lines into individual words
            words = line.split()
            line_words = []
            for word in words:
                #print(word)
                if "$" in word:
                    word = word.replace('$',' ') # have to set it equal otherwise it doesnt change
                    print(word)
                line_words.append(word)
            para_lines.append(line_words)
        structured_content.append(para_lines)

    print(structured_content)

    # i think there is something here but it should work