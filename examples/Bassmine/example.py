import gsapi.GSBassmineAnalysis as bassmine
import gsapi.GSBassmineMarkov as markov
import json
import csv
import random

# STYLE DICTIONARY
style = {1: 'booka_shade', 2: 'mr_scruff'}

# SELECT STYLE
style_id = 2

bass_path = '../../corpus/bassmine/' + style[style_id] + '/bass'
drum_path = '../../corpus/bassmine/' + style[style_id] + '/drums'

# Output folder
_path = 'output/' + style[style_id] + '/'


# Analyse corpus and build Markov model
MM, kick_patterns= bassmine.corpus_analysis(bass_path, drum_path)
# Normalize transition matrices
MM.normalize_model()

# EXAMPLES OF MARKOV INTERLOCKING CONSTRAINED MODEL
# Given a Kick pattern generate a NHMM with interlocking constraint
target = kick_patterns[random.randint(0,len(kick_patterns)-1)]
print target
#print kick_patterns
target = [8,8,8,9,8,8,9,0]
markov.constrainMM(MM,target)

# Create variation model
target_bass = [5,5,-5,5,5,-5,5,5]
markov.variationMM(MM,target_bass)

#  Uncomment to create models and export to pickle. REQUIRED to add new collections and use them in Max app.
# Export to pickle files
bassmine.write2pickle('initial', MM.get_initial(),_path)
bassmine.write2pickle('temporal', MM.get_temporal(),_path)
bassmine.write2pickle('interlocking', MM.get_interlocking(),_path)


#########################################
#  DEBUG

"""
print "Initial"
print pitch_model.get_initial()
print "Temporal"
print pitch_model.get_temporal()

print "Interlocking"
print MM.get_interlocking()
"""
##########################################
#  EXPORT TO CSV
"""
with open('initial.csv', 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(MM.get_initial())

with open('temporal.csv', 'wb') as f:
	writer = csv.writer(f)
	temp = MM.get_temporal()
	for row in temp:
		writer.writerow(row)

with open('interlocking.csv', 'wb') as f:
	writer = csv.writer(f)
	temp = MM.get_interlocking()
	for row in temp:
		writer.writerow(row)
"""