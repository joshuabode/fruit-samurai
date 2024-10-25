"""
This is a stub for COMP16321 Coursework 01.
Do not edit or delete any lines given in this file that are marked with a "(s)".
(you can move them to different lines as long as you do not change the overall structure)

Place your code below the comments marked "#Your code here" and before the pass for that method.

Each method is documented to explain what work is to be placed within it.

NOTE: You can create as many more methods as you need. However, you need to add 
self as a parameter of the new method and  to call it with the prefix self.name 

"""

class Basics:#(s)
    # ---Section 1 --- #

    def read_dict(self):
        with open('dictionary.txt', 'r') as file:
            eng_dict = file.read().splitlines()

        return eng_dict

    def clean_words(self, str_list):
        symbols = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', 
                   '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
        words = []
        for w in str_list:
            w = w.lower()
            w = ''.join([c for c in w if c not in symbols])
            words.append(w)
        return words

    #(Task 1.1)
    def read_file(self):#(s)
        """
            Read the contents of the text file paragraph.txt and return it as a single string.

            Returns: 
                str: The content of the text file as a single string
        """
        #Your code here
        with open('paragraph.txt', 'r') as file:
            return file.readline()
        pass#(s)
    
    # ---Section 2 --- #

    #(Task 2.1)
    def length_of_file(self, file_string):#(s)
        """
            Calculate the length of the text string from Task 1.1

            This method calculates the total number of characters in the provided text string,
            including letters, numbers, symbols, and whitespace, and returns the result as an integer.
        
            Parameters:
                file_string (str): The text string from Task 1.1

            Returns:
                int: The length of the text string, including all characters.
        """
        #Your code here
        return len(file_string)
        pass#(s)

    #(Task 2.2)
    def lower_case_count(self, file_string):#(s)
        """
            Calculate the total number of lower case letters (i.e. a-z) in the text string from Task 1.1

            This method calculates the total number of lower case letters in the provided text string and returns the result as an integer
        
            Parameters:
                file_string (str): The text string from Task 1.1

            Returns:
                int: The count of lower case letters.
        """
        #Your code here
        res = 0
        for char in file_string:
            if 96 < ord(char) < 123:        # Checks if the ASCII encoding of the number corresponds to a lowercase letter
                res += 1
        return res
        pass#(s)

    #(Task 2.3)
    def upper_case_merge(self, file_string):#(s)
        """
            Find all upper case letters (i.e. A-Z) in the text string from task 1.1 and merge these into a single string

            This method finds all upper case letters and merges them into a singular string of upper case letters. E.g. "thIs Sentence OF a feW wordS" will return "ISOFWS"
        
            Parameters:
                file_string (str): The text string from Task 1.1

            Returns:
                str: The upper case letters as a single string
        """
        #Your code here
        res = ""
        for char in file_string:
            if 64 < ord(char) < 91:        # Checks if the ASCII encoding of the number corresponds to a UPPERCASE letter
                res += char
        return res
        pass#(s)

    #(Task 2.4)
    def digits_sum(self, file_string):#(s)
        """
            Sum all digits in the text string from task 1.1

            Find all digits in the text string and sum them together. Each digit must be treated as an individual digit. E.g. i.e. if there is a 1 then 23 then this will be treated as 1+2+3 and not 1+23 
        
            Parameters:
                file_string (str): The text string from Task 1.1

            Returns:
                int: The sum of all digits in the file
        """
        #Your code here
        res = 0
        for char in file_string:
            if 47 < ord(char) < 58:        # Checks if the ASCII encoding of the number corresponds to a digit
                res += int(char)
        return res
        pass#(s)

    # ---Section 3 --- #

    #(Task 3.1)
    def specific_character(self, file_string, word, letter):#(s)
        """
            Reports the n'th letter in the m'th word of the paragraph as a string. If m'th word is not present in the dictionary file then return False

            For something to constitute a word it must appear in the dictionary.txt file, this comparison is case insensitive. You should remove additional punctuation such as a ' or , when determining if something is a word or not. E.g. "python's" would be read as "pythons" and that should be checked against the dictionary.
        
            Parameters:
                file_string (str): The text string from Task 1.1
                word (int): An integer denoting which word
                letter (int): An integer denoting which letter

            Returns:
                str: The letter in position 'letter' of 'word', if the input is valid
                bool: False if the input is invalid
        """
        #Your code here
        words = [w for w in self.clean_words(file_string.split(" "))]
        english_dict = self.read_dict()
        words = [w for w in words if w in english_dict]
        print(words)
        try:
        	return words[word-1][letter-1]
        except IndexError:
        	return False


        pass#(s)

    #(Task 3.2)
    def word_display(self, file_string, length):#(s)
        """
            Returns a list of all words in the text string from task 1.1 which are of size 'length' or longer

            For something to constitute a word it must appear in the dictionary.txt file
        
            Parameters:
                file_string (str): The text string from Task 1.1
                length (int): An integer denoting the length of words to be counted

            Returns:
                arr[str]: A list of all words of size 'length' or longer as individual strings
        """
        #Your code here
        english_dict = self.read_dict()
        original_words = [w for w in file_string.split(" ")]
        clean_indicies = []
        res = []
        for i, w in enumerate(original_words):
        	if self.clean_words([w])[0] in english_dict:
        		clean_indicies.append(i)
   
        for i in clean_indicies:
        	if len(self.clean_words([original_words[i]])[0]) >= length:
        		res.append(original_words[i])
        		
        return res
       
        pass#(s)

    #(Task 3.3)
    def letter_count(self, file_string, letters):#(s)
        """
            Returns a count of all letters (i.e. a-z) irrespective of case, ignoring those specified.

            Specified letters are provided in the letters parameter.
        
            Parameters:
                file_string (str): The text string from Task 1.1
                letters (arr[str]): An array of strings denoting which letters to not count

            Returns:
                int: The count of all letters ignoring those specified 
        """
        #Your code here
        count = 0
        file_string = file_string.lower()
        letters = [l.lower() for l in letters]
        for char in file_string:
            if char.isalpha() and char not in letters:
                count += 1

        return count
        pass#(s)

    #(Task 3.4)
    def find_replace(self, file_string, old_substring, new_substring):#(s)
        """
            Find all occurrences of a substring and replace then with the provided new substring

            Directly replace the old substring with the new one with no further changes and return the whole text. If there are no occurrences of the substring then nothing will be replaced.
        
            Parameters:
                file_string (str): The text string from Task 1.1
                old_substring (str): The substring which is to be replaced
                new_substring (str): The substring which is used in the place of the removed substring

            Returns:
                str: The contents of the text as a single string
        """
        #Your code here
        old_len = len(old_substring)
        i = file_string.find(old_substring)
        while True:
            if i != -1:
                file_string = file_string[:i] + new_substring + file_string[i+old_len:]
                i = file_string.find(old_substring)
            else:
                break
        return file_string
        pass#(s)


if __name__ == '__main__':#(s)

    # Testing Wikipedia's featured article's first paragraph
    test_a = Basics()
    a_string = test_a.read_file() 
    print(test_a.clean_words("Determine and return the character which is found as the n'th letter within the m'th word of the paragraph (n & m given as parameter). Display words but only those words of length n or longer".split(" ")))
    print(test_a.read_dict()[:10])
    
    print(test_a.word_display(a_string, 9))                                 # Self-Test: ✅
    print(test_a.letter_count(a_string, ['j', 'o', 's', 'h']))              # Self-Test: ✅                
    print(test_a.find_replace(a_string, 'He', 'THIS USED TO SAY "HE"'))     # Self-Test: ✅    
                
                    
             

    pass#(s)
