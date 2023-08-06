Project Title: Contagious Naive Bayes(CNB)

With the increase in online social media interactions, the true identity of user profiles becomes increasingly doubtful. 
Fake profiles are used to engineer perceptions or opinions as well as to create online relationships under false pretence. 
Natural language text – how the user structures a sentence and uses words – provides useful information to discover expected patterns, 
given the assumed social profile of the user. We expect, for example, different word use and sentence structures from teenagers to those of adults. 

Sociolinguistics is the study of language in the context of social factors such as age, culture and common interest. Natural language processing (NLP),
provides quantitative methods to discover sociolinguistic patterns in text data. Current NLP methods make use of a multinomial naive Bayes classifier to 
classify unseen documents into predefined sociolinguistic classes. One property of language that is not captured in binomial or multinomialmodels, 
is that of burstiness. Burstiness defines the phenomenon that if a person uses a word, they are more likely to use that word again. 
Thus, the independence assumption between respective counts of the same word is relaxed. The Poisson distribution family captures this phenomenon and 
in the field of biostatistics, it is often referred to as contagious distributions (because the counts between contagious diseases are not independent). 
In this pacakge, the count independence assumption of the naive Bayes classifier is relaxed by replacing the baseline multinomial likelihood function with 
a Poisson likelihood function. 

This packages thus allows the user to make use of contagious naive Bayes as an alternative to the readily available techniques.  


Getting Started:
The package is available online for use within Python 3 enviroments.

The installation can be performed through the use of a standard 'pip' install command, as provided below: 

#####

Prerequisites

The package has several dependencies, namely: 

-pandas
-numpy
-re
-nltk
-warnings
-sklearn
-BeautifulSoup


Example Usage:
Installation;

Run the following 


Implementation;


Results;




Built With:
Google Collab - Web framework
Python - Programming language of choice
Pypi - Distribution


Authors:
Iena Petronella Derks


Co-Authors:
Alta de Waal
Luandrie Potgieter
Ricardo Marques


License:
This project is licensed under the MIT License - see the LICENSE.md file for details.


Acknowledgments:
University of Pretoria
Center for Artifcial Intelligence Research (CAIR)
