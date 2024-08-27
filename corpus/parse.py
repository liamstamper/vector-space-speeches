#!/usr/bin/python3
# Alberto Maria Segre
#
# Copyright 2014, The University of Iowa.  All rights reserved.
# Permission is hereby given to use and reproduce this software 
# for non-profit educational purposes only.
import re
from math import sqrt, log

# Stop words should not be considered in the text.
SW = ( 'a','able','about','across','after','all','almost','also','am','among',
       'an','and','any','are','as','at','be','because','been','but','by','can',
       'cannot','could','dear','did','do','does','either','else','ever',
       'every','for','from','get','got','had','has','have','he','her',
       'hers','him','his','how','however','i','if','in','into','is','it',
       'its','just','least','let','like','likely','may','me','might',
       'most','must','my','neither','no','nor','not','of','off','often',
       'on','only','or','other','our','own','rather','said','say','says',
       'she','should','since','so','some','than','that','the','their',
       'them','then','there','these','they','this','tis','to','too',
       'twas','us','wants','was','we','were','what','when','where',
       'which','while','who','whom','why','will','with','would',
       'yet','you','your' )
# Contractions should be expanded in the text.
CC = ( ("aren't","are not"),("can't","can not"),
       ("could've","could have"),("couldn't","could not"),
       ("couldn't've","could not have"),("didn't","did not"),
       ("doesn't","does not"),("don't","do not"),
       ("hadn't","had not"),("hadn't've","had not have"),
       ("hasn't","has not"),("haven't","have not"),
       ("he'd","he had"),("he'd've","he would have"),
       ("he'll","he will"),("he's","he is"),("how'd","how did"),
       ("how'll","how will"),("how's","how has"),("I'd","I had"),
       ("I'd've","I would have"),("I'll","I will"),
       ("I'm","I am"),("I've","I have"),("isn't","is not"),
       ("it'd","it had"),("it'd've","it would have"),
       ("it'll","it will"),("it's","it is"),("let's","let us"),
       ("ma'am","madam"),("mightn't","might not"),
       ("mightn't've","might not have"),("might've","might have"),
       ("mustn't","must not"),("must've","must have"),
       ("needn't","need not"),("not've","not have"),
       ("o'clock","of the clock"),("shan't","shall not"),
       ("she'd","she had"),("she'd've","she would have"),
       ("she'll","she will"),("she's","she is"),
       ("should've","should have"),("shouldn't","should not"),
       ("shouldn't've","should not have"),("that's","that is"),
       ("there'd","there had"),("there'd've","there would have"),
       ("there're","there are"),("there's","there is"),
       ("they'd","they had"),("they'd've","they would have"),
       ("they'll","they will"),("they're","they are"),
       ("they've","they have"),("wasn't","was not"),
       ("we'd","we had"),("we'd've","we would have"),
       ("we'll","we will"),("we're","we are"),("we've","we have"),
       ("weren't","were not"),("what'll","what will"),
       ("what're","what are"),("what's","what is"),
       ("what've","what have"),("when's","when is"),
       ("where'd","where did"),("where's","where is"),
       ("where've","where have"),("who'd","who had"),
       ("who'll","who will"),("who're","who are"),
       ("who's","who is"),("who've","who have"),
       ("why'll","why will"),("why're","why are"),
       ("why's","why is"),("won't","will not"),
       ("would've","would have"),("wouldn't","would not"),
       ("wouldn't've","would not have"),("y'all","you all"),
       ("y'all'd've","you all would have"),
       ("you'd","you had"),("you'd've","you would have"),
       ("you'll","you will"),("you're","you are"),
       ("you've","you have"),("-"," ") )
# Presidents
P = ( 'adams','arthur','bharrison','buchanan','bush','carter','cleveland',
      'clinton','coolidge','eisenhower','fdroosevelt','fillmore','ford',
      'grant','gwbush','hayes','hoover','jackson','jefferson','johnson',
      'jqadams','kennedy','lbjohnson','lincoln','madison','mckinley',
      'monroe','nixon','obama','pierce','polk','reagan','roosevelt',
      'taft','taylor','truman','tyler','vanburen','washington', 'wilson' )
# Filelists
F = ( 'adams0.txt','adams1.txt','adams2.txt','adams3.txt',
      'arthur0.txt','arthur1.txt','arthur2.txt','arthur3.txt',
      'bharrison0.txt','bharrison1.txt','bharrison2.txt','bharrison3.txt',
      'buchanan0.txt','buchanan1.txt','buchanan2.txt','buchanan3.txt',
      'bush0.txt','bush1.txt','bush2.txt','bush3.txt',
      'carter0.txt','carter1.txt','carter2.txt','carter3.txt',
      'cleveland0.txt','cleveland1.txt','cleveland2.txt','cleveland3.txt',
      'clinton0.txt','clinton1.txt','clinton2.txt','clinton3.txt',
      'coolidge0.txt','coolidge1.txt','coolidge2.txt','coolidge3.txt',
      'eisenhower0.txt','eisenhower1.txt','eisenhower2.txt','eisenhower3.txt',
      'fdroosevelt0.txt','fdroosevelt1.txt','fdroosevelt2.txt','fdroosevelt3.txt',
      'fillmore0.txt','fillmore1.txt','fillmore2.txt','fillmore3.txt',
      'ford0.txt','ford1.txt','ford2.txt','ford3.txt',
      'grant0.txt','grant1.txt','grant2.txt','grant3.txt',
      'gwbush0.txt','gwbush1.txt','gwbush2.txt','gwbush3.txt',
      'hayes0.txt','hayes1.txt','hayes2.txt','hayes3.txt',
      'hoover0.txt','hoover1.txt','hoover2.txt','hoover3.txt',
      'jackson0.txt','jackson1.txt','jackson2.txt','jackson3.txt',
      'jefferson0.txt','jefferson1.txt','jefferson2.txt','jefferson3.txt',
      'johnson0.txt','johnson1.txt','johnson2.txt','johnson3.txt',
      'jqadams0.txt','jqadams1.txt','jqadams2.txt','jqadams3.txt',
      'kennedy0.txt','kennedy1.txt','kennedy2.txt','kennedy3.txt',
      'lbjohnson0.txt','lbjohnson1.txt','lbjohnson2.txt','lbjohnson3.txt',
      'lincoln0.txt','lincoln1.txt','lincoln2.txt','lincoln3.txt',
      'madison0.txt','madison1.txt','madison2.txt','madison3.txt',
      'mckinley0.txt','mckinley1.txt','mckinley2.txt','mckinley3.txt',
      'monroe0.txt','monroe1.txt','monroe2.txt','monroe3.txt',
      'nixon0.txt','nixon1.txt','nixon2.txt','nixon3.txt',
      'obama0.txt','obama1.txt','obama2.txt','obama3.txt',
      'pierce0.txt','pierce1.txt','pierce2.txt','pierce3.txt',
      'polk0.txt','polk1.txt','polk2.txt','polk3.txt',
      'reagan0.txt','reagan1.txt','reagan2.txt','reagan3.txt',
      'roosevelt0.txt','roosevelt1.txt','roosevelt2.txt','roosevelt3.txt',
      'taft0.txt','taft1.txt','taft2.txt','taft3.txt',
      'taylor0.txt','taylor1.txt','taylor2.txt','taylor3.txt',
      'truman0.txt','truman1.txt','truman2.txt','truman3.txt',
      'tyler0.txt','tyler1.txt','tyler2.txt','tyler3.txt',
      'vanburen0.txt','vanburen1.txt','vanburen2.txt','vanburen3.txt',
      'washington0.txt','washington1.txt','washington2.txt','washington3.txt',
      'wilson0.txt','wilson1.txt','wilson2.txt','wilson3.txt' )
# Unknowns
U = ( 'unknown0.txt','unknown1.txt','unknown2.txt','unknown3.txt','unknown4.txt' )

# Dot product of two vectors represented as lists.
def dproduct(v1, v2):
   return(sum([ pair[0]*pair[1] for pair in zip(v1,v2) ]))

# Open a file for input and return a dictionary containing the stemmed
# word frequencies. C is the corpus term dictionary, which is
# implicitly updated.
def parseFile(filename, C):
   D = {} # Term dictionary for this document
   n = 0  # Length of this document sans stopwords
   infile = open(filename, 'r')
   for line in infile:
      for (x, y) in CC:
        line = line.lower().replace(x, y)
      # Parse the line, updating document dictionary D, corpus
      # dictionary C and n as you go.
      n = parseLine(line, n, D, C)
   infile.close()
   # Return document length and term dictionary. C, the corpus
   # dictionary, is updated implicitly but not explicitly returned.
   return(n, D)

def parseUnknown(filename):
   D = {} # Term dictionary for this document
   n = 0  # Length of this document sans stopwords
   infile = open(filename, 'r')
   for line in infile:
      for (x, y) in CC:
        line = line.lower().replace(x, y)
      # Parse the line, updating document dictionary D and n as you
      # go.
      n = parseLine(line, n, D)
   infile.close()
   # Return document length and term dictionary. C, the corpus
   # dictionary, is updated implicitly but not explicitly returned.
   return(n, D)

# Parse a line from the input file, stripping punctuation, applying
# the stemmer and updating both the document dictionary D and the
# corpus dictionary C as you go.  Returns an updated value for n, the
# length of the entire document, having implicitly updated C and
# D. Note: if C is None, then it is not updated.
def parseLine(S, n, D, C=None):
   for w in [ stemmer(w) for w in [ w.strip('".,:;!?()') for w in S.split() ] if w not in SW ]:
      n = n + 1
      if w in D:
         # Not new to either D or C.
         D[w] = D[w] + 1
         if C != None:
            C[w] = C[w] + 1
      elif C!= None and w in C:
         # New to D, but not C.
         D[w] = 1
         if C != None:
            C[w] = C[w] + 1
      else:
         # New to both D and C.
         D[w] = 1
         if C != None:
            C[w] = 1
   # Return updated number of words in document.
   return(n)

# Simple stemmer. Would benefit from ordering of endings as well as use of regular expressions
# to avoid shortening a word too much. For example, "faiths" -> "fai+th+s" is too short. Would
# also be good to add final 'e' in cases where certain endings are removed.
def stemmer(word):
   endings = ['able','al','ance','ant','ar','ary','ate','ement','ence','ent','er','ess',
              'ible','ic','ify','ine','ion','ism','iti','ity','ive','ize','ly','ment',
              'or','ou','ous','th','ure']
   if word[-3:] == 'ies' and word[-4:] not in ['eies', 'aies']:
      word = word[:-3] + 'y'
   if word[-2:] == 'es' and word[-3:] not in ['aes', 'ees', 'oes']:
      word = word[:-1]
   if word[-2:] == "'s":
      word = word[:-2]
   if word[-1:] == 's' and word[-2:] not in ['us', 'ss', 'ys']:
      word = word[:-1]
   for ending in endings:
      if word[-len(ending):] == ending:
         word = word[:-len(ending)]
   return(word)

# Return top k items in dictionary by value (here, the word frequency).
def topK(D,k):
   L = [ (item, D[item]) for item in D.keys() ]
   return(sorted(L, reverse=True, key=lambda x: x[1])[0:k])

# Build a vector for a document. You'll need the document's length
# dltfd[0], the document's term frequency index dlftd[1], the word
# vector, the word vector document count, and the number of documents
# in the corpus, D.
def buildVector(dltfd, vwords, vcount, D):
   vector = []
   for word in vwords:
      try:
         # dltfd[1][word[0]] is the number of times word appears in the document
         # dltfd[0] is the document length
         # D is the size of the corpus
         # vcount[word[0]] is the number of documents in D with word
         vector.append((dltfd[1][word[0]]/dltfd[0])*log(D/(1+vcount[word[0]])))
      except:
         vector.append(0)
   # Convert result to a unit vector
   norm = sqrt(sum([ weight*weight for weight in vector ]))
   return([ weight/norm for weight in vector ])

def buildVectors(L,k=10):
   # ctfd is the corpus term frequency dictionary
   ctfd = {}
   # dtfds are the document length and term frequency dictionaries;
   # ctfd is updated as you go as well. indexed by document, these
   # are (n, tfd) pairs.
   dltfds = { file:parseFile(file, ctfd) for file in L }
   #print(ctfd)
   # these are the selected vector words
   vwords = topK(ctfd,k)
   #print("Using vector words: " + str(vwords))
   vcount = { word[0]:len([True for file in L if word[0] in dltfds[file][1]]) for word in vwords }
   #print("Using vector counts: " + str(vcount))
   return(ctfd, dltfds, vwords, vcount, len(L), { file[:-4]:buildVector(dltfds[file],vwords,vcount,len(L)) for file in L })

# Identify an unknown
def identify(file, ctfd, dltfds, vwords, vcount, D, vectors):
   vector = buildVector(parseUnknown(file), vwords, vcount, D)
   return( { target:dproduct(vector,vectors[target]) for target in vectors.keys() } )

V = buildVectors(F,35) # ctfd, dltfds, vwords, vcount, D, vectors
for file in U:
   print("Identifying " + file)
   s = [ (p[:-1],v) for (p,v) in sorted(identify(file, V[0], V[1], V[2], V[3], V[4], V[5]).items(), key=lambda V: V[1])[-10:] ]
   s.reverse()
   print(s)
   
