**DB Test - Comments from Denis Maurin**

**1. Approach to the problem**

The goal is to ask 2 questions in natural language (English) and return the answers using dbpedia, a structured query frontend of Wikipedia supporting SparQL and RDF data.

_Question 1: "How old is Tony Blair?"_

_Question 2: "What is the birth place of David Cameron?"_

In order to keep the complexity of the solution to a reasonable level, I assume that only these 2 questions are supported by the software and that other questions will have to be coded or defined manually.

1.1 Parse the question using regular expressions

The goal is to identify the different parts of the sentence using regular expressions and a NLP framework.

1.2 Identity recognition

Once we can identify the words corresponding to a person (or a thing for ex), we can use DBpedia to return the page corresponding to this entry. We will then form a SparQL query to return the date of birth for example identified as a particular URI.

1.3 Rendering of the result

The result of the SparQL query (JSON) is then converted into a simple string by retaining the English version only.

**2 Prototype code in Python (NLTK, Quepy)**

NLTK and Quepy libraries provide a simple and elegant way to transform natural language to database queries. A similar approach may be implemented in Scala or Java but would take significantly longer and would fall outside the scope of this exercise.

The complete code is available in my Github repository: https://github.com/denismaurin/DBPedia.git

NLTK [http://www.nltk.org](http://www.nltk.org): NLTK is one of the most preeminent platform for Natural Language Processing (NLP) and incorporates a comprehensive suite of text processing libraries. For classification, tokenization, stemming, tagging, parsing, etc.

Quepy [http://quepy.rtfd.org](http://quepy.rtfd.org) : This library leverages NLTK to transform natural language questions to database queries. Quepy supports SparQL (and MQL). The demo application shipped with Quepy queries DBPedia already. Under the hood Quepy uses Refo to process regular expressions for object sequences (and not only strings).

I have extended Quepy to implement the two questions of the test. As we will see later on, the Dbpedia ontology is loaded as well as the standard w3 owl, rdf syntax, foaf, etc.


_Question 1: "How old is Tony Blair?"_

We specify a domain specific language related to birth date and referencing the correct property:

``` 
class BirthDateOf(FixedRelation):
relation = "dbpprop:birthDate"
reverse = True
```

Then we define the question and the associated regular expression in a special way (Refo library):

```
class HowOldIsQuestion(QuestionTemplate):
regex = Pos("WRB") + Lemma("old") + Lemma("be") + Person() + Question(Pos("."))
def interpret(self, match):
birth_date = BirthDateOf(match.person)
return birth_date, "age"
```

We can see how the regex is built. A lemmatiser will match the variants (inflicted forms) of the verb "to be" for example. Also a Person() object is defined earlier in the code as a regex based on standard speech tags (http://stackoverflow.com/questions/1833252/java-stanford-nlp-part-of-speech-labels):

```
regex = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))
```

In the instance of our question, the following SparQL is produced. It is quite straightforward.

```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX quepy: <http://www.machinalis.com/quepy#>

SELECT DISTINCT ?x1 WHERE {  
?x0 rdf:type foaf:Person.  
?x0 rdfs:label "Tony Blair"@en.  
?x0 dbpprop:birthDate ?x1.
}
```

Final stage is to parse the birth date and calculate the age. A simple utility function will do the job by parsing the JSON answer, extract the date, parse year, month, day and calculate the number of years to the present day.

```
birth_date = results["results"]["bindings"][0][target]["value"]
bd2 = birth_date.split("+")
year, month, days = (bd2[0]).split("-")
birth_date = datetime.date(int(year), int(month), int(days))
now = datetime.datetime.utcnow()
now = now.date()
age = now - birth_date
print "{}".format(age.days / 365)
```

Result is: 61

_Question 2: What is the birth place of David Cameron?"_

A similar approach is used for this second question. 

Domain specific language (DSL):

```
class BirthPlaceOf(FixedRelation):
relation = "dbpedia-owl:birthPlace"
reverse = True
```

Regular expression:

```
class WhatIsBirthPlace(QuestionTemplate):
regex = Lemma("what")+ Lemma("be") + Question(Lemmas("the birth place of")) + Person() + \
Question(Pos("."))
def interpret(self, match):
birth_place = BirthPlaceOf(match.person)
label = LabelOf(birth_place)
return label, "place"
```

In order to capture the "Where is person X born?" variant, we could also add the following regex

```
regex = Lemma("where")+ Lemma("be") + Person() + Lemma("born") + Question(Pos("."))
```

The following SparQL is generated. It is also very straightforward.

```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX quepy: <http://www.machinalis.com/quepy#>

SELECT DISTINCT ?x2 WHERE {  
?x0 rdf:type foaf:Person.  
?x0 rdfs:label "David Cameron"@en.  
?x0 dbpedia-owl:birthPlace ?x1.  
?x1 rdfs:label ?x2.
}
```

I have been lacking the time to apply some modifications to return the birthplace as a URI (x1 in the query) and to query DBpedia to resolve the country (dbpedia-owl:country returning dbpedia:United\_Kingdom with label United Kingdom). The result of the query is not exactly aligned with the expected value (England vs. United Kingdom) but close enough for the sake of this exercise:

Response: London, England

Other questions could be matched successfully:
"What was the birth place of Alexandre Dumas?"

Response: France, Villers-Cotterêts

As well as variants captured by the second regex:
"Where was Victor Hugo born?"

Response: Besançon, French First Republic
