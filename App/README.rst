App
===

The building of the Android app is done via Buildozer. Accordingly the main settings are done in the
buildozer.spec file. The file is well documented.

Due to licensing restrictions I could not distribute the icons with the source code. That means as long as
nobody creates custom icons for me that I could distribute with the code you have to provide some icons on
your own if you want to compile the app.

Concretely you have to provide the following icon files(works best with icons in a 1:1 aspect ratio) in the subfolder
data:

1. data/plus.png (plus sign that is used for adding items or increasing the amount)
2. data/minus.png (minus sign for decreasing the amount)
2. data/refresh_on.png (icon that refreshes the shopping list by fetching it from the remote server)
3. data/edit.png (edit mode off) and data/edit_on.png (edit mode on)

After providing these files you have to change line 19 in main.py
to point towards your servers address.

Finally the Android package can be build via:

buildozer -v android debug

You will find the .apk file in the created bin folder. Transfer this file to your Android device and enjoy:)
