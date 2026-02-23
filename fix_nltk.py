import nltk

print("Downloading required NLTK resources...")
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('brown')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('conll2000')
    print("Done! Try running main.py again.")
except Exception as e:
    print(f"Error: {e}")