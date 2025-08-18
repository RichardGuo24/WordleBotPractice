import random
# To install colorama, run the following command in your VS Code terminal:
# python3 -m pip install colorama
from colorama import Fore, Back, Style, init
init(autoreset=True) #Ends color formatting after each print statement

from wordle_secret_words import get_secret_words
from valid_wordle_guesses import get_valid_wordle_guesses


valid_wordle_guesses = get_valid_wordle_guesses()
secret_words = get_secret_words()

alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def basic_check(guess: str, secret_word: str) -> bool:
    return (guess.isalpha() and len(guess) == 5 and guess.upper() in valid_wordle_guesses)

def get_feedback(guess: str, secret_word: str) -> str:

    ### BEGIN SOLUTION
    guess = guess.lower()
    secret_word = secret_word.lower()
    
    if(not basic_check(guess, secret_word)):
        return "-----"

    copy_secret = list(secret_word)
    return_string = ["-", "-", "-", "-", "-"]

    
    for i in range(len(guess)):
        if (guess[i] == secret_word[i]):
            return_string[i] = guess[i].upper()
            copy_secret[i] = None

    for k in range(len(guess)):
        if(guess[k] in copy_secret) and (guess[k] != secret_word[k]):
            return_string[k] = guess[k]
            copy_secret[copy_secret.index(guess[k])] = None
        if(guess[k] not in copy_secret and guess[k] in alphabet):
            alphabet.remove(guess[k])
    
    return ''.join(return_string)



# def get_AI_guess(guesses: list[str], feedback: list[str], secret_words: set[str], valid_guesses: set[str]):
    
#     for word in list(secret_words):  
#         if not all(get_feedback(guesses[i], word) == feedback[i] for i in range(len(guesses))):
#             secret_words.remove(word)
            
#     #also true if secret_words is two words
#     if (any(fb == "-OUND" for fb in feedback) or any(fb == "-ATCH" for fb in feedback) or any(fb == "-ASTE" for fb in feedback) or any(fb == "-O-ER" for fb in feedback)or any(fb == "-IGHT" for fb in feedback))and (len(guesses) <= 4):
    
#         highest_amount = 0
#         return_string = ""
#         for word in list(secret_words):
#             current = 0
#             for letter in word:
#                 if(letter in alphabet):
#                     current += 1
#             if current > highest_amount:
#                 highest_amount = current
#                 return_string = word
#         if return_string:
#             print("Best word based on letter frequency:", return_string)
#             return return_string
#     elif(secret_words):
#         return random.choice(list(secret_words))
#     return random.choice(list(valid_guesses))

    #first find out if feedback has only 3 or 4 greens
def get_AI_guess(guesses: list[str], feedback: list[str], secret_words: set[str], valid_guesses: set[str]):

    # Filter out words that do not match the feedback
    for word in list(secret_words):
        if not all(get_feedback(guesses[i], word) == feedback[i] for i in range(len(guesses))):
            secret_words.remove(word)

    tricky_patterns = ["-OUND", "-ATCH", "-ASTE", "-O-ER", "-IGHT"]

    if any(any(fb.startswith(pattern) for fb in feedback) for pattern in tricky_patterns) and len(guesses) <= 4:
        print("yes")
        highest_score = 0
        best_word = ""

        for word in secret_words:
            current_score = current_score = len(set(word) & set(alphabet))
            if current_score > highest_score:
                highest_score = current_score
                best_word = word

        if best_word:
            return best_word

    elif secret_words:
        # Prioritize words with the most unguessed letters
        best_word = max(secret_words, key=lambda word: len(set(word) & set(alphabet)))
        return best_word

    # Fall back to a random valid guess if no secret words remain
    best_word = random.choice(list(valid_guesses))
    return best_word



def secret_word_setter():
    return random.choice(list(secret_words))

def coloring(feedback: str, player_guess):
    result = ""
    for j in range(len(feedback)):
        if feedback[j].isupper():
            result = result + Back.GREEN + player_guess[j].upper()
        elif feedback[j].islower():
            result = result + Back.YELLOW + player_guess[j].upper()
        elif feedback[j] == "-":
            result = result + Back.BLACK + player_guess[j].upper()
    return result

if __name__ == "__main__":
    init()

    win = 0
    lose = 0
    score = 0.0

    # Create a local copy of secret words for iteration
    all_secret_words = list(secret_words)  # Convert to list to avoid modification issues

    
    
    for secret_word in list(all_secret_words):
        list_of_all_guesses = []
        aiguess = []
        feedback = []
        aifeedback = []
        winorlose = False
        player_guess = None
        
        alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

        for i in range(6):
            if player_guess is None or player_guess == "slate":
                
                if(player_guess == "slate"):
                    player_guess = "pound"
                else: 
                    player_guess = "slate"
                
                aiguess.append(player_guess)
                aifeedback.append(get_feedback(player_guess, secret_word))
            else:
                player_guess = get_AI_guess(aiguess, aifeedback, all_secret_words, set(valid_wordle_guesses))
                aiguess.append(player_guess)
                aifeedback.append(get_feedback(player_guess, secret_word))

            if player_guess.lower() == secret_word.lower():
                winorlose = True
                feedback = list(get_feedback(player_guess, secret_word))
                list_of_all_guesses.append(coloring(feedback, player_guess))
                win += 1
                score += i + 1
                break
            elif basic_check(player_guess, secret_word):
                feedback = get_feedback(player_guess, secret_word)
                list_of_all_guesses.append(coloring(feedback, player_guess))


            #print("\n\n")

        if not winorlose:
            for j in list_of_all_guesses:
                print(j)
            lose += 1
            score += 6
            print("You lost. The correct word was: " + secret_word, "You still had: ", + len(all_secret_words))
            print(alphabet)
            
        all_secret_words = list(secret_words)   

    print("Wins:", win, "Losses:", lose, "Score:", score / (win + lose))
    
    #idea is run 2 ai's at the same time so that we can max out accuracy
