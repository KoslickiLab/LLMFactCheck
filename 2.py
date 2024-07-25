with open('data/RTX-KG2.8.4c_sentence_data.csv', 'r') as fin:
    data = fin.read().splitlines(True)
with open('data/RTX-KG2.8.4c_sentence_data.csv', 'w') as fout:
    fout.writelines(data[1:])
	#data/RTX-KG2.8.4c_labeled_records.csv
	#data/RTX-KG2.8.4c_sentence_data.csv
	#data/RTX-KG2.8.4c_triple_data.csv
