import re
from math import log, sqrt

# Presidents
P = ( 'adams','arthur','bharrison','buchanan','bush','carter','cleveland', 
      'clinton','coolidge','eisenhower','fdroosevelt','fillmore','ford',
      'grant','gwbush','hayes','hoover','jackson','jefferson','johnson',
      'jqadams','kennedy','lbjohnson','lincoln','madison','mckinley',
      'monroe','nixon','obama','pierce','polk','reagan','roosevelt',
      'taft','taylor','truman','trump','tyler','vanburen','washington', 'wilson' )
# Unknown Speeches
U = ( 'unknown0','unknown1','unknown2','unknown3','unknown4' )

# Stop words
SW={ 'a','able','about','across','after','all','almost','also','am','among','an',
     'and','any','are','as','at','be','because','been','but','by','can',
     'cannot','could','dear','did','do','does','either','else','ever','every','for',
     'from','get','got','had','has','have','he','her','hers','him','his',
     'how','however','i','if','in','into','is','it','its','just','least',
     'let','like','likely','may','me','might','most','must','my','neither','no',
     'nor','not','of','off','often','on','only','or','other','our','own',
     'rather','said','say','says','she','should','since','so','some','than','that',
     'the','their','them','then','there','these','they','this','tis','to','too',
     'twas','us','wants','was','we','were','what','when','where','which','while',
     'who','whom','why','will','with','would','yet','you','your' }

# Contractions, possessives, etc.
REGEXP=((r"\'s", ""), (r"won\'t", "will not"), (r"can\'t", "can not"), 
        (r"n\'t", " not"), (r"\'re", " are"), (r"\'d", " would"), (r"\'ll", " will"), 
        (r"\'t", " not"), (r"\'ve", " have"), (r"\'m", " am"))

class Corpus():
    def __init__(self, directory="corpus/"):
        # Directory where the speech text files are located.
        self.directory=directory
        # Dictionary of Speech objects indexed by speech name.
        self.speeches={}
        # Word frequency distribution (less stop words) for the Corpus
        # (will be computed from individual Speech wfreqs). Keys are
        # words, values are word counts over the Corpus.
        self.wfreq={}
        # Document frequency distribution (less stop words).  Keys are
        # words, values are document counts over the Corpus.
        self.dfreq={}
        # Vector template: ordered list of high frequency words used
        # in identification.
        self.template=[]

    # Corpus().addSpeech(name) adds a speech to the corpus. The name
    # argument is used to locate the file containing the speech in
    # self.directory, and is also used to identify the speech in the
    # dictionary of speeches within the corpus.
    def addSpeech(self, name):
        # Read in a Speech object, initialize it, and it to the
        # corpus (unless its already there).
        if name not in self.speeches:
            # Index new Speech() object by name in self.speeches. Note
            # that speech files are found in self.directory and always
            # carry a .txt file extension.
            self.speeches[name]=(Speech("{}{}.txt".format(self.directory, name)))
 
            # Incorporate word frequencies from new speech into
            # corpus-level word frequencies.
            self.updateFreqs(self.speeches[name])

    # Corpus().updateFreqs(speech) updates both the Corpus document
    # frequency and word frequency values using the word frequency
    # distribution of the specified speech as your guide. If the word
    # is in Speech.wfreq, it means it is in the document (i.e., the
    # speech you are incorporating); it also increases Corpus.wfreq.
    def updateFreqs(self, speech):
        for word in speech.wfreq:
            try:
                self.dfreq[word] += 1
                self.wfreq[word] += speech.wfreq[word]
            except:
                self.dfreq[word] = 1
                self.wfreq[word] = speech.wfreq[word]

    # Find the top k most frequently used words in the Corpus that do
    # not appear in every document. 
    # 
    # Note: if there is only one Speech 
    # in the Corpus, then there will be no words in topK (because they
    # all appear in all of the Corpus documents).
    def topK(self, k):
        L = [ (word, self.wfreq[word]) for word in self.wfreq.keys() if self.dfreq[word] != len(self.speeches) ]
        for i in range(k):
            j = i + L[i:].index(max(L[i:], key=lambda x: x[1]))
            L[i],L[j] = L[j],L[i]
        return([ record[0] for record in L[:k] ])

    # Corpus().createVectors(k) finds the top k words and use them to
    # define a vector template, then, tell each speech in the corpus
    # to calculate its corresponding vector.
    #
    # Note if there are too few speeches in the Corpus, or they all
    # rely on very similar vocabularies, then you may not find k words
    # that don't appear in all of the Speeches. In this case, your
    # vector will be shorter, and even empty (certainly the case when
    # there is only 1 Speech in Corpus).
    def createVectors(self, k):
        self.template = self.topK(k)
        for i in self.speeches.keys():
            self.speeches[i].makeVector(self.template, self.dfreq, len(self.speeches))

    # Corpus().identify(mystery, k, j) takes a mystery filename and
    # matches it against all the speeches using TDIDF vectors of
    # length k, returning the j closest matches.
    def identify(self, mystery, k, j):
        # Create new vectors if k is different.
        if len(self.template) != k:
            self.createVectors(k)
        # Read in the unidentified speech.
        unidentified = Speech("{}{}.txt".format(self.directory, mystery))
        unidentified.makeVector(self.template, self.dfreq, len(self.speeches))
        return(sorted([ (self.speeches[s].cosSimilarity(unidentified), s) for s in self.speeches.keys() ], reverse=True)[:j])

# The Speech() class represents an speech, read from the specified
# filename.  
class Speech():
    # Most of the work takes place in the constructor, which must open
    # the file, read in the text, and store three representations of
    # the text in instance variables as follows.
    #
    # self.text is the simplified text, still upper/lower case, but
    # with possessives and contractions removed, excess punctuation
    # removed, and both ! and ? replaced with . the only allowed
    # puncutation.
    #
    # self.sentences is a list of sentences constructed from self.text
    #
    # self.words is a list of words from self.txt with no punctuation.
    #
    # In addition, the constructor produces word frequency counts for
    # the document using non-stopwords only.
    #
    # Note: Makes use of several "helper" functions.
    def __init__(self, filename):
        # The expandWord(word) helper function is used to apply a
        # series of regular experssion substitutions to expand
        # contractions and flush possessives. The goal here is to
        # eliminate all of the embedded "'" characters.
        def expandWord(word):
            i = 0
            while "'" in word and i < len(REGEXP):
                word =re.sub(REGEXP[i][0], REGEXP[i][1], word)
                i = i+1
            return(word)

        # The expandText(text) helper function "normalizes" the input
        # text, producing a cleaned up version consisting of words
        # without any embedded "'". Case and other elements are left
        # unchanged.
        def expandText(text):
            return(''.join([expandWord(word) for word in text.split()]))

        # The flushMarks(m) helper function is used to remove
        # extraneous punctuation marks while replacing ? and ! with
        # . to have a uniform EOS mark.
        def flushMarks(m):
            if m.group(1) in ('--', '-', '—', '_'):
                return(' ') 
            elif m.group(1) in ('(', ')', ',', ':', '\'', '"', '...'):
                return('')
            elif m.group(1) in ('?', '!'):
                return('.')

        # Here is the body of the __init__() method. It starts by
        # reading in the text of the speech, expanding any
        # contractions and dropping any possessives. It also strips
        # punctuation at word boundaries except for '.!?'  which
        # define sentences, and are replaced with periods.
        with open(filename, 'r') as infile:
            self.text=re.sub("\\s+"," ",re.sub('(--|-|—|_|\\(|\\)|,|:|\'|"|\\.\\.\\.|\\?|!)',flushMarks,expandText(infile.read()))).strip()

        # Next, create a list of sentences, including stopwords, and
        # leaving the case unchanged.
        self.sentences=[ sentence.strip() for sentence in self.text.split('.') if sentence != '' ]

        # Next, create a list of lower-case words in sequential order,
        # stripping any remaining punctuation (only periods remain)
        self.words=[ word.strip('.').strip() for word in self.text.lower().split() if word != '.' ]

        # Finally, create a word frequency index in self.wfreq based
        # on the words in self.words but ignoring any stop words in
        # SW.
        
        self.wfreq = {}
        for word in self.words:
            if word not in SW:
                try:
                    self.wfreq[word] += 1
                except:
                    self.wfreq[word] = 1

    # Speech().makeVector(template, dfreq, N) takes a template (an
    # ordered list of words), the dfreq dictionary of document
    # frequencies (number of documents in the corpus containing the
    # key word), N, the total number of documents in the corpus and
    # produces a TF/IDF vector.
    #
    # To compute the TF/IDF vector value, multiple the normalized
    # per-document TF (the term's word frequency in the document
    # divided by the number of term appearences -- that is, words
    # less stop words -- in the document) times the inverse
    # document frequency adjusted to avoid divide-by-zero errors
    # (i.e., log(N/(1+dfreq(t))).
    def makeVector(self, template, dfreq, N):
        self.vector = []
        for word in template:
            try:
                self.vector.append((self.wfreq[word]/len(self.words))*log(N / (1+dfreq[word])))
            except:
                self.vector.append(0.0)

    # Cosine similarity of two vectors is computed as the dot product
    # divided by the cross product of the two vectors, defined as the
    # product of vector magnitudes (the squareroot of the sum of
    # squares of the vector components).
    def cosSimilarity(self, other):
        # Helper function returns the vector magnitude of a vector,
        # which is the square root of the sum of the squares of the
        # vector elements.
        def vectorMagnitude(vector):
            return(sqrt(sum([ val*val for val in vector ])))
        # Compute the dot product and divide by the product of the
        # individual vector magnitudes.
        # Calculate the dot product of the two vectors    
        dot_product = sum([ pair[0]*pair[1] for pair in zip(self.vector, other.vector) ])
        
        # Calculate the magnitudes of the two vectors
        self_magnitude = vectorMagnitude(self.vector)
        other_magnitude = vectorMagnitude(other.vector)
        
        # Add a small value to the denominator to avoid division by zero
        epsilon = 1e-6
        denominator = (self_magnitude * other_magnitude) + epsilon
        
        # Calculate the cosine similarity
        return dot_product / denominator


if __name__ == '__main__':
    c=Corpus()
    for p in P:
        for i in range(4):
            c.addSpeech(p + str(i))
    for u in U:
        print("Mystery speech {} is closest to: {}".format(u[-1], c.identify(u, 2000, 4)))
    
