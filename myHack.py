import detectEnglish, vigenereCipher
import re, more_itertools, itertools, collections, time
import numpy as np

ALPHABET = np.array(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


def hacker(sourceText):
  processedText = prepareText(sourceText)
  spacing = repeatedSequencesSpacings(processedText)
  mostLikelyLengths = spacingsFactorsSorted(spacing)
  for keyLength in mostLikelyLengths:
    attempt = attemptWithKeyLength(processedText, sourceText, keyLength)
    print(keyLength, attempt)
    if attempt != None:
      return attempt
    
def prepareText(source):
  source = source.upper()
  regex = re.compile('[^A-Z]')
  processedText = regex.sub('', source)
  return processedText

def repeatedSequencesSpacings(sourceText):
  repeatedSeqSpacings = np.empty(0, dtype=np.int8)
  for seqLen in range(2, 6):
    allSequences = list(more_itertools.windowed(sourceText, seqLen))
    allDuplicatedSeqIndeces = list_duplicates(allSequences)
    for duplicateIndeces in allDuplicatedSeqIndeces.values():
      spacings = np.diff(duplicateIndeces)
      spacings = np.delete(spacings, np.where(spacings < seqLen))
      repeatedSeqSpacings = np.concatenate((repeatedSeqSpacings, spacings))
  repeatedSeqSpacings = np.unique(repeatedSeqSpacings)
  return repeatedSeqSpacings

def list_duplicates(seq):
    sequences = collections.defaultdict(list)
    for i,item in enumerate(seq):
        sequences[item].append(i)
    return sequences

def spacingsFactorsSorted(arr):
  factorsFrequency = collections.Counter()
  for spacing in arr:
    factors = getNumFactors(spacing)
    for factor in list(factors):
      factorsFrequency[factor] += 1
  del factorsFrequency[1]
  sortedFactors = mostCommonKeys(factorsFrequency)
  return sortedFactors

def getNumFactors(num):
  if num == 2 or num == 3:
    return np.array([1, num])
  result = np.array(num)
  for factor in range(1, num//2):
    if num%factor == 0:
      result = np.append(result, factor)
  return result

def attemptWithKeyLength(processedText, sourceText, keyLength):
  mostLikelyLetters = LetterDecypher(processedText, keyLength)
  for key in itertools.product(*mostLikelyLetters):
    key = ''.join(key)
    decypheredText = vigenereCipher.decryptMessage(key, sourceText)
    isEnglish = detectEnglish.isEnglish(decypheredText)
    if isEnglish:
      return decypheredText
  return None

def LetterDecypher(processedText, keyLength):
  charGroups = [nthChars(processedText, keyLength, i) for i in range(keyLength)]
  bestLettersForEachGroup = [collections.Counter() for i in range(keyLength)]
  for i, group in enumerate(charGroups):
    letterScores = collections.Counter()
    for letter in ALPHABET:
      decypheredGroup = vigenereCipher.decryptMessage(letter, group)
      frequencyScore = frequencyAnalysis(decypheredGroup)
      bestLettersForEachGroup[i][letter] = frequencyScore
  for i, bestLettersForGroup in enumerate(bestLettersForEachGroup):
    bestLettersForGroup = getRidOfUncommon(bestLettersForGroup)
    bestLettersForEachGroup[i] = bestLettersForGroup
  return bestLettersForEachGroup

def frequencyAnalysis(string):
  charCounter = collections.Counter(string)
  sortedChars = mostCommonKeys(charCounter)
  firts6 = sortedChars[:6]
  last6 = sortedChars[-6:]
  common6 = np.array(['E','T','A','O','I','N'])
  uncommon6 = np.array(['V','K','J','X','Q','Z'])
  frequencyScore = 0
  frequencyScore += len(np.intersect1d(firts6, common6))
  frequencyScore += len(np.intersect1d(last6, uncommon6))
  return frequencyScore

def nthChars(string, n, bias):
  return string[bias::n]

# def getRidOfUncommon(counter, iterations):
#   for i in range(iterations):
#     average = np.ceil(np.average(list(counter.values())))
#     counter = collections.Counter({k:v for k,v in counter.items() if v>= average})
#   return counter

def getRidOfUncommon(counter):
  theBestLetters = []
  borderFreq = counter.most_common(1)[0][1] - 3
  previousFreq = 0
  for char, freq in counter.most_common(len(counter)):
    if (freq != previousFreq and len(theBestLetters) > 4) or freq < borderFreq:
      break
    theBestLetters.append(char)
    previousFreq = freq
  return theBestLetters

def mostCommonKeys(counter):
  sortedCounter = counter.most_common(len(counter))
  sortedCounter = list(zip(*sortedCounter))[0]
  return list(sortedCounter)



source = """Albert Einstein (14 March 1879 – 18 April 1955) was a German-born theoretical physicist who is widely held to be one of the greatest and most influential scientists of all time. Best known for developing the theory of relativity, Einstein also made important contributions to quantum mechanics, and was thus a central figure in the revolutionary reshaping of the scientific understanding of nature that modern physics accomplished in the first decades of the twentieth century.[1][5] His mass–energy equivalence formula E = mc2, which arises from relativity theory, has been called "the world's most famous equation".[6] He received the 1921 Nobel Prize in Physics "for his services to theoretical physics, and especially for his discovery of the law of the photoelectric effect",[7] a pivotal step in the development of quantum theory. His work is also known for its influence on the philosophy of science.[8][9]
Born in the German Empire, Einstein moved to Switzerland in 1895, forsaking his German citizenship (as a subject of the Kingdom of Württemberg)[note 1] the following year. In 1897, at the age of seventeen, he enrolled in the mathematics and physics teaching diploma program at the Swiss federal polytechnic school in Zürich, graduating in 1900. In 1901, he acquired Swiss citizenship, which he kept for the rest of his life. In 1903, he secured a permanent position at the Swiss Patent Office in Bern. In 1905, he submitted a successful PhD dissertation to the University of Zurich. In 1914, he moved to Berlin in order to join the Prussian Academy of Sciences and the Humboldt University of Berlin. In 1917, he became director of the Kaiser Wilhelm Institute for Physics; he also became a German citizen again, this time as a subject of the Kingdom of Prussia.[note 1]
In 1933, while he was visiting the United States, Adolf Hitler came to power in Germany. Horrified by the Nazi "war of extermination" against his fellow Jews,[10] Einstein decided to remain in the US, and was granted American citizenship in 1940.[11] On the eve of World War II, he endorsed a letter to President Franklin D. Roosevelt alerting him to the potential German nuclear weapons program and recommending that the US begin similar research. Einstein supported the Allies but generally viewed the idea of nuclear weapons with great dismay.[12]
In 1905, sometimes described as his annus mirabilis (miracle year), Einstein published four groundbreaking papers.[13] These outlined a theory of the photoelectric effect, explained Brownian motion, introduced his special theory of relativity—a theory which addressed the inability of classical mechanics to account satisfactorily for the behavior of the electromagnetic field—and demonstrated that if the special theory is correct, mass and energy are equivalent to each other. In 1915, he proposed a general theory of relativity that extended his system of mechanics to incorporate gravitation. A cosmological paper that he published the following year laid out the implications of general relativity for the modeling of the structure and evolution of the universe as a whole.[14][15] The middle part of his career also saw him making important contributions to statistical mechanics and quantum theory. Especially notable was his work on the quantum physics of radiation, in which light consists of particles, subsequently called photons. With the Indian physicist Satyendra Nath Bose, he laid the groundwork for Bose-Einstein statistics. For much of the last phase of his academic life, Einstein worked on two endeavors that proved ultimately unsuccessful. First, he advocated against quantum theory's introduction of fundamental randomness into science's picture of the world, objecting that "God does not play dice".[16] Second, he attempted to devise a unified field theory by generalizing his geometric theory of gravitation to include electromagnetism too. As a result, he became increasingly isolated from the mainstream of modern physics.
In a 1999 poll of 130 leading physicists worldwide by the British journal Physics World, Einstein was ranked the greatest physicist of all time.[17] His intellectual achievements and originality have made the word Einstein broadly synonymous with genius.[18]"""
txt = vigenereCipher.encryptMessage('eisntein', source)
s = time.time()
hak = hacker(txt)
print(hak)
print(time.time() - s)
