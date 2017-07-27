This script can be used to place an order using OCAPI.  Here are instructions for installing on OS X:

1.  Install Homebrew by executing the following in a terminal window:

	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	
2.  Install python by executing the following in a terminal window:

	brew install python3

3.  Install the requests module for Python by executing the following in a terminal window:

	pip3 install requests
	
4.  Add the JSON object in sample.ocapi.settings.json to your OCAPI settings in the business manager.

	Administration >  Site Development >  Open Commerce API Settings
	
	Select Shop and Global from the two drop down menus.  Note:  you can only have one version of OCAPI active at one time.  You may receive permission errors when accessing the APIs if you have a different version of OCAPI configured as well.
	
5.  Modify the variables at the top of test.py to contain a valid URL, username (email address), password, and user email.  You may also need to update the product id if the product ID in the script is not available for purchase on your site.

6.  Execute the script by running the following in a terminal window:

	python3 test.py
	
You should see some information written to the screen with the tokens that are passed back and forth between the client and server.  You should be able to see an order in the business manager under the site you specified in your URL.