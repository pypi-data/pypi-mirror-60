# MTSB

MTSB (Movie Tweet Sentiment Boxoffice) is a python module that collects tweets about movies, performs a sentiment analysis and correlates it with the boxoffice result of the 7 days after the movie release.

## Features

* Collect tweets about movies
* Creates hashtags for each movie
* Performs sentiment analysis on those tweets using Google's API or Textblob and returns the average score and the average magnitude
* Gets boxoffice data from boxofficemojo
* Performs correlation between the sentiment analysis and boxoffice data

## Requirements

* Python >= 3.5 (Might work on older versions but it has not been tested)
* The package has only been tested on Linux, with the following docker compose environment: https://gitlab.com/aletundo/data-management-lab
* All module dependencies are installed on installation, but you will also need:
    * You need to have set up correctly ntlk module: https://www.nltk.org/install.html
    * Performed at least once "ntlk.download()"
    * Already have API keys for tweet collection: https://developer.twitter.com/en.html
    * If you plan on using Google's API you lready need to have API keys for Google Natural Language service: https://cloud.google.com/natural-language/docs/setup
* You also need to have the following services installed (tested on Linux system)
    * Jupyter-lab
    * MongoDB
    * Nifi
    * Kafka
    
## Installation

In order to install MTSB you can simply:

```
pip install mtsb
```

## Docs

* tweet_collector()

Collect tweets about movies. It lets you choose between movies released in 2019 and releasing in 2020. It then creates a list of hashtags based on the movie's name and top actors and uses it to collect tweets from twitter.

```
import mtsb

mtsb.tweet_collector()
```

* sentiment()

Performs sentiment analysis on collected tweets using Google's API or Textblob and returns the average score and the average magnitude.

```
import mtsb

mtsb.sentiment()
```

* sentiment_perc()

Performs sentiment analysis on collected tweets using Google's API or Textblob and returns a the percentage of positive tweets.

```
import mtsb

mtsb.sentiment_perc()
```

* sentiment_boxoffice_all()

Creates a dataframe with the following info for each movie:
    * Movie title and genres
    * Average mean of the tweets' scores and magnitudes
    * Percentage of positive and negative labelled tweets (if score==0 is labelled as positive)
    * Sum of the boxoffice of the 7 days after the movie release

```
import mtsb

mtsb.sentiment_boxoffice_all()
```

* spearman_corr(df)

Performs a spearman correlation using the df returned by sentiment_boxoffice_all().

```
mtsb.spearman_corr(df)
```

## Links

* PyPI: https://pypi.org/project/mtsb/

## Acknowledgements

Useful python libraries used:
* [imdbpy library](https://github.com/alberanid/imdbpy/ "imdbpy library title")
* [ntlk library](https://github.com/nltk/nltk "ntlk library title")
* [beautifulSoup library](https://pypi.org/project/beautifulsoup4/ "beautifulSoup library title")
* [Textblob library](https://github.com/sloria/TextBlob "Textblob library title")
* [Google-cloud library](https://github.com/googleapis/google-cloud-python "Google-cloud library title")

## Licence

MIT licensed. See the bundled [LICENSE](https://github.com/federicodeservi/mtsb-analyzer/blob/master/LICENSE "LICENSE title") file for more details. 
