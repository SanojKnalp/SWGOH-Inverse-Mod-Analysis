# SWGOH-Inverse-Mod-Analysis
The idea behind this repo was to create an inverse mod searching tool to allow players to search for characters that need certain mods.

How to install it:
You need Python and a Python IDE, i recommend Spyder(ask ChatGPT for help in case you struggle).
Once you got it, you need to install requests, beautifulsoup4 and tkinter(command is pip install requests beautifulsoup 4 tkinter(Linux Ubuntu)).
Then you can easily run it using spyder.

I only tested it using Linux, but Mac and Windows should work as well.

You can also use it as a discord bot, you basically just need to install the required packages(pip install <package_name>). Once done, setup your discord bot and add the code to bot.run('Token') by replacing 'Token' with the actual token of your bot.

The command to run it is !find_mod <set> <shape> <stat>. You can either search for all three or just for sets. The possible sets are triangle, arrow, cross and circle. For sets and stats, always remember to write the full name, so for example 'critical damage' instead of 'crit damage'. 

The typing in itself should not be case-sensitive, but please don't overdo it.

Also there is currently a graphical issue with the bot that causes a formatting issue when going over 2000 characters, so i recommend not to use for speed and health sets + speed arrows cause they will be over 2000 characters. I'm working on a fix.


