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

This packages thus allows the user to make use of contagious naive Bayes as an alternative to the readily available techniques to perform binary text classification.  


Getting Started:
The package is available online for use within Python 3 enviroments.

The installation can be performed through the use of a standard 'pip' install command, as provided below: 

pip install Contagious-Naive-Bayes==1.0.0

Prerequisites

The package has several dependencies, namely: 

-pandas

-numpy

-re

-nltk

-warnings

-sklearn

-BeautifulSoup


Function description:

The function is named "CNB".

The function can take 5 possible arguments, two of which are required, and the remaining 3 being optional. 

The required arguments are: 

-Train_Matrix(A matrix containing the observations on which the classification model will be trained.)

-Test_Matrix(A matrix containing observation which will be used to test the performance of the model.)

The optional requirements are: 

-norm(A True/False flag which specifies whether document length normalization must be applied. The method of document length normalization utilized for this package this that of
Pseduo-Length normalization. The default is set to False.)

-pseudo_len(Should document length normalization be required, this specifies the length to which the documents should be normalized to. The default is 100, while any user input is 
required to be postive.)

-c1(This is the first smoothing parameter required to perform document length normalization. The default is set to 0.001.)

-c2(This is the second smoothing parameter required to perform document length normalization. The default is set to 1.)


Output:

The function provides the output in two components, firstly it provides a table containing the index of the observations, the posteriors calculated per possible class for each observations
as well as the predicted class and the actual class of each observation. 

Secondly, the function provides several performance metrics, the metrics utilized are accuracy, precision, recall and the F1 score. 


Example Usage:

Installation;

Run the following command within a Python command window:

> pip install Contagious-Naive-Bayes==1.0.0


Implementation;

Import the package into the relevant python script, with the following: 

> from Contagious_NB import Classification as func

> Call the function:

Possible examples of calling the function are as follows:

> x_cnb = func.CNB(train_matrix,test_matrix)

> x_cnb = func.CNB(train_matrix,test_matrix, norm = True,  pseduo_len = 100, c1 = 0.001, c2 = 1)


Results;

The output obtained appears as follows: 

The Contagious Naive Bayes has executed.

The total runtime was:  174.4942226409912 seconds

The Posterior Probabilities obtained are as follows: 

               0          1  Predicted  Actual

Index                                         

19518 -29.730902 -21.774997          1       0

3482   -4.785887  -4.445511          1       1

17305 -16.137118 -17.162267          0       1

9134  -28.772151 -27.929778          1       0

19435 -18.030701 -17.489797          1       1

5379   -0.477393  -0.175956          1       0

11752 -13.191803 -10.240028          1       1

19813 -14.608706 -11.396712          1       0

18037 -25.245713 -26.544791          0       1

16755 -20.097580 -21.674529          0       0

8937   -7.544991  -7.938454          0       0

20023 -10.300211 -11.100099          0       0

...          ...        ...        ...     ...

The performance metrics obtained are as follows:   
                 
Accuracy   0.622500

Precision  0.739777

Recall     0.710714

F1         0.724954


Built With:

Google Collab - Web framework

Python - Programming language of choice

Pypi - Distribution


Authors:
Iena Petronella Derks

https://github.com/iEna101/Contagious-Naive-Bayes


Co-Authors:

Alta de Waal

Luandrie Potgieter

Ricardo Marques


License:
This project is licensed under the MIT License - see the LICENSE.md file for details.


Acknowledgments:

University of Pretoria

Center for Artifcial Intelligence Research (CAIR)
