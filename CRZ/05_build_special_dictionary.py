# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  numpy, re, os, pandas                             |
# -------------------------------------------------------------------- |
# Build Slovak dictionary from words in contracts                      |
# which are not part of standard Slovak corpus                         |
# -------------------------------------------------------------------- |
import os
import re
import hunspell
import operator

# úprava - nevyužité

slovak_alphabet = 'aáäbcčdďeéfghiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž'

def parse_text(text):
	text = text.casefold()
	words = []

	new_word = ''
	word = True
	for char in text:
		if char in slovak_alphabet:
			new_word = new_word + char
			word = True
		else:
			if word:
				words.append(new_word)
				new_word = ''
			word = False

	return words

# Import standard Slovak dictionary
normal_SK  = os.path.join(os.getcwd(), 'Dicts\\sk_SK')
english_US = os.path.join(os.getcwd(), 'Dicts\\en_US')

hunspell_normal  = hunspell.Hunspell(normal_SK, normal_SK)
hunspell_english = hunspell.Hunspell(english_US, english_US)

def check_normal(word):
	return hunspell_normal.spell(word) or hunspell_english.spell(word)

# Find all text contracts
find_txt    = re.compile('txt')
working_dir = os.getcwd()+'\\IT_contracts_text\\'

contracts = [f for f in os.listdir(working_dir) if os.path.isfile(os.path.join(working_dir, f))]
contracts_txt = [f for f in contracts if (len(find_txt.findall(f))>0)]

N = len(contracts_txt)
N_words = 0

new_words = dict()
# Analyse words in every text contract
for i, contract in enumerate(contracts_txt):
	print('Analysing contract: ', contract, ' ', i+1, 'out of', N)

	fo = open(working_dir+contract, 'r', encoding = 'utf-8')
	lines = fo.readlines()
	fo.close()

	text = ''

	for line in lines:
		text += line.casefold().replace('\n',' ')

	del lines

	words = parse_text(text)
	for word in words:
		if not check_normal(word):
			if word in new_words:
				new_words[word] +=1
			else:
				new_words[word] = 1

	print('Number of words:', len(words), '| New words:', len(new_words))
	N_words += len(words)

print('Total number of words: ', N_words)
print('Total new words: ', len(new_words))

sorted_new_words = sorted(new_words.items(), key=operator.itemgetter(1), reverse=True)
# Keep only words if there number of occurrences is at least 100
sorted_new_words = [word[0] for word in sorted_new_words if word[1] > 5]

print('Filtered new words: ',len(sorted_new_words))

fo = open('sk_SK_special.dic', 'w', encoding = 'utf-8')
fo.write(str(len(sorted_new_words))+'\n')

for word in sorted_new_words:
	fo.write(word+'\n')

fo.close()
