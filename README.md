# Synai

DevWeb course project realised by Mme. Kim Aurore Biloni, M. Ludovic Herbelin &  M. Thibault Haldenwang

The goal of this project is to create a website that will feature statistics using the Spotify API for the users. Users will be able to select a data source from Spotify (Artist, Album, Song, Playlist, History) and the website will analyse the audio features of the selected audio feed given by the API. The app will recommend songs related to those values that the user can save as a playlist in his Spotify profile.

The features analysed include for example :
- Danceability
- Acousticness
- Valence
- etc.

The analysis results will then be saved in the database and the user can see it on the History page. Each analysis will be displayed with the data values as text and charts.

The user can also see some statistics on his Dashboard page.

## Installation

1. Download the project : `git clone https://github.com/HE-Arc/Synai.git`
2. Create a env in the root folder
3. Activate it
4. Load the requirements : `pip install -r requirements.txt`

## Update

1. Create the migrations : `python manage.py makemigrations`
2. Apply the migrations : `python manage.py migrate`
3. Start the local server: `python manage.py runserver`

The webapp now run locally on your server ! Enjoy ☺

## SCSS modifications

We use sass to make our app look good. For it, you can install [Sass](https://sass-lang.com/) with [Npm](https://www.npmjs.com/). If you installd a "make" tool, you can `make compile-scss` and it will update the sass files.
