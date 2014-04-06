install pytz package before running:(use following commmand if you have pip)
    sudo pip install pytz

Please update readme if you change anything, I could not run the server and had to check all changes
(* carpoolsen *)

Formatting of search results
Footer screwed on some pages.


VERY IMPORTANT
EVERYONE DO THIS
ASAP
RIGHT NOW

make a file "paths.py" in your carpoolsen folder (besides manage.py)
inside paths.py, paste  (WITH THE SLASH)

    cpspath=/path-to-the-folder-parent-to-your-carpoolsen-folder/'


for example
if my carpoolsen folder is here
    /home/rishav/carpoolsen/

then path.py should contain
    cpspath='/home/rishav/'
    
Then create /media/propics in the folder which cpspath points to.

for example

    mkdir /home/rishav/media/
    mkdir /home/rishav/media/propics/
    
then change permissions of these created folders by running (for example)

    chmod 777 /home/rishav/media/
    chmod 777 /home/rishav/media/propics/
    
=======================
=======================



To Do:

1. Implement remaining views. check views.py for more info.
2. Integrate front end with backend
3. Add SMS support
4. Add Facebook integration
5. Add Google Maps Api (frontend work, just suggestion prompts, etc. Nothing to be done in backend mostly. Lets see)


(* <!-- Rating table not opening but working fine. --> *)
(* <!-- Dashboard list in decreasing order. --> *)
NEW_TODO

<!-- CHECK EDIT POST -->
<!-- Receipt shows footer text -->
<!-- LoginVerify Validate -->
<!-- Gmaps -->
<!-- Edit_post date-time issue -->
<!-- Dropdown not working on settings page -->
<!-- Photos and links in footer -->
Install pytz package
//Outbox


Bugs found by me(Abhishek Kumar){
(* 	edit profile not working *)
(* 	footer is playing hide and seek *)
(* 	header dropdown not working on invite_page *)
(*	if logged in a user should not be able to open signup_page *)
(* 	if logged in a user should not be able to open signup_page *)
(* 	after editing my post on edit_post_page, submitting throws an error (DATE TIME FORMAT FIXING, VINODH is DOING THAT) *)
(* 	@iphone there are no checks on post_form for total_seats, car_type , when submitting without changing these values throws server error *)

	sugestions:
		post_page different icon/photo for each entry, same ones create confusion (BTW dummy profile photo is great!!)
		on post_form cost_per_seat field Rs should be written on the right hand side.
		an additional check before cancel post

	question:
(* 		I could not delete a trip that has started. When will it get deleted?? After an hour *)

}
 
