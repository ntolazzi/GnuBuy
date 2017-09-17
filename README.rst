Gnubuy
======

This repository contains the server and client code for a **synchronized shopping list application**
which is meant to be used in a cooperative manner.
My initial incentive for the work was that I was never satisfied
with the existing applications in the typical AppStores for two primary reasons. First, I dislike
advertisement in apps and the corresponding security risks. Second, I want to keep my data as private as possible
and therefore decided to go with a self hosted solution. Additionally it is a nice and maybe even useful first project
for Android development.


The client code is build using the `Kivy <https://kivy.org/>`_ framework for Python which provides all necessary UI elements.
Furthermore it is easy to build an Android package from the code(the code is very portable and
runs without any changes also on a linux pc). You can find further info and the build instructions in the
folder App.


The server code is build using `Flask <http://flask.pocoo.org/>`_ and implements an incomplete RESTful API.
Build instructions can be found in the folder Server.