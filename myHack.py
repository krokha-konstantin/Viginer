import detectEnglish, vigenereCipher
import re, more_itertools, itertools, collections, time
import numpy as np

ALPHABET = np.array(list('ABCDEFGHIJKLMOPQRSTUVWXYZ'))


def hacker(sourceText):
  processedText = prepareText(sourceText)
  spacing = repeatedSequencesSpacings(processedText)
  mostLikelyLengths = spacingsFactorsSorted(spacing)
  for keyLength in mostLikelyLengths:
    attempt = attemptWithKeyLength(processedText, sourceText, keyLength)
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
  borderFreq = counter.most_common(1)[0][1] - 2
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



source = """`Giovan Battista Bellaso, born of a distinguished family in 1505, was the son of Piervincenzo, a patrician of Brescia. Piervincenzo owned a house in town and a suburban estate in Capriano del Colle, in a neighborhood called Fenili Belasi. The estate included the Holy Trinity chapel, where a chaplain was paid a regular salary and provided with firewood. The Bellaso family coat of arms displayed three red-tongued gold lion heads in side view on a blue field. Bellaso earned a degree in civil law from the University of Padua in 1538. French author Blaise de Vigenère reported that Bellaso served as a secretary for Cardinal Rodolfo Pio di Carpi and credited him with inventing the reciprocal table, now called the Della Porta table. However, Bellaso never mentioned the Cardinal in his writings and explained he was working for Cardinal Duranti in Camerino in 1550. During this time, Bellaso needed to use secret correspondence for state affairs while his master was in Rome for a conclave. Skilled in research and mathematics, Bellaso became involved in secret writing, a practice highly admired in Italian courts, especially the Roman Curia. This was a golden age for cryptography, and Bellaso was one of many secretaries who experimented with new systems due to intellectual curiosity or practical necessity. His cipher system was groundbreaking and considered unbreakable for centuries. As a student of ciphers, he mentioned many enthusiasts, including prominent figures and "great princes." In 1552, he met Count Paolo Avogadro, Count Gianfrancesco Gambara, and the renowned writer Girolamo Ruscelli, also an expert in secret writing. These colleagues urged him to publish a complete and well-instructed version of his reciprocal table, which had been circulating in loose-leaf form. Copies of these tables still exist in private collections in Florence and Rome."""
txt = vigenereCipher.encryptMessage('viginer', source)
s = time.time()
hak = hacker(txt)
print(hacker(txt))
print(time.time() - s)
