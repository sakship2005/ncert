from nlp_engine.preprocessing.cleaner import clean_text


sample_text = """
Now those fellows out
there will have the right to say to you, ‘How is it;
you pretend to be Frenchmen, and yet you can neither
speak nor write your own language?’

But you are not the worst, poor little Franz.
"""


cleaned = clean_text(sample_text)

print("\nCLEANED TEXT")
print("=" * 60)
print(cleaned)