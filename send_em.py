#Imports

import sendgrid
import os
from tkinter import *
from sendgrid.helpers.mail import *
import requests
import urllib.request as urlget
from PIL import Image, ImageTk, ImageOps

#Global Variables
root = Tk()
gmaps_url_partial = "https://www.googleapis.com/geolocation/v1/geolocate?key="
gmaps_key = "AIzaSyBMvIrD-VjSdROdoJ-E1EtAhq8prM-tE2U"
sg_api_key = "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"
sg = sendgrid.SendGridAPIClient(apikey=sg_api_key)
jsonFlickrApi = lambda x: x

#Google Maps (Gets Longitude & Latitude)
location_request = requests.post(gmaps_url_partial+gmaps_key).text
location = eval(location_request)["location"]
lat, lon = location["lat"], location["lng"]

###
#Flickr API
###

def selected(event,obj):
	global selected_image
	color = obj.cget("background")
	for each in displayed_photos:
		each.config(background="white")
	if color != "orange":
		obj.config(background="orange")
		selected_image = obj
	else:
		selected_image = None

#Gets List of Photo Urls
n_requests = 50
flickr_url_partial = "https://api.flickr.com/services/rest/?method=flickr.photos.search"
flickr_key = "53ec1bbf7a22b24e05abb00975caa67a"
params = "&lat="+str(lat)+"&lon="+str(lon)+"&format=json"+"&per_page="+str(n_requests)+"&api_key="+str(flickr_key)+"&text=scenic"
flickr_request = requests.post(flickr_url_partial+params).text
flickr_request_dic= eval(flickr_request)
photo_data =  flickr_request_dic["photos"]["photo"]
photo_urls = ["http://farm" + str(data["farm"]) + ".staticflickr.com/" + str(data["server"]) + "/" + str(data["id"]) + "_" + str(data["secret"]) + ".jpg" for data in photo_data]

#Empty Initializations
photo_bar = Frame(root,height=20,width = 130)
listed_images = 0
checked_images = 0
displayed_photos = []
selected_image = None
names_dic={None:""}
print(1)
#Filters & Adds images
while listed_images < 4:
	name_of_pic = "pic"+str(listed_images)+".jpg"
	urlget.urlretrieve(photo_urls[checked_images], name_of_pic)
	original = Image.open(name_of_pic)
	height, width = original.size
	if float(height)/float(width) > 0.5 and float(height)/(width) < 1.5:
		print(listed_images)
		listed_images += 1
		image = ImageTk.PhotoImage(Image.open(name_of_pic).resize((150,150)),(150,150))
		photo = Label(photo_bar,image = image, bd = 5)
		displayed_photos.append(photo)
		names_dic[photo] = photo_urls[checked_images]
		photo.pic = image
		photo.pack(side=RIGHT)
	else:
		original.close()
	checked_images += 1

#Photo Selection/Highlighting
for photo in displayed_photos:
	photo.bind("<Button-1>",(lambda photo : lambda event: selected(event,photo))(photo))

###
#Tkinter
###

def get_content(obj):
	return obj.get(1.0, END)
	
#Sendgrid
def send_mail():
	if selected_image:
		from_email = Email(get_content(from_add))
		print()
		print("Sent to",get_content(to_add))
		print()
		to_email = Email(get_content(to_add))
		subject = get_content(header)
		remainder_html = "<img src='"+names_dic[selected_image]+"'><p>"
		content = Content("text/html", remainder_html+get_content(main)+"</p>")
		mail = Mail(from_email, subject, to_email, content)	
		response = sg.client.mail.send.post(request_body=mail.get())
		user_message.config(text="",background="white")
	else:
		user_message.config(text="Please select an image!",background="yellow")
def placeholder(event,obj,text):
	if get_content(obj) == "\n":
		obj.insert(INSERT,text)
def clear_placeholder(event,obj,reg):
	if get_content(obj) == reg + "\n":
		obj.delete(1.0, END)
def tab_focus(event, next_focus):
	next_focus.focus_set()
	return "break"

#Components
user_message=Label(root,text="",height=1,width=20)
from_add = Text(root,height = 1, width = 130, highlightcolor="#ccccff", padx = 5, pady = 2)
to_add = Text(root, height = 1, width = 130, highlightcolor="#ccccff", padx = 5, pady = 2)
header = Text(root, height = 1, width = 130, highlightcolor="#ccccff", padx = 5, pady = 2)
main = Text(root, height = 30, width = 130, padx = 10, pady = 15, borderwidth = 0, highlightcolor="white")
send = Button(root, text="Send email!", command = send_mail)

#Initial Text
from_add.insert(INSERT,"Your Email Address")
to_add.insert(INSERT,"Recipient")
header.insert(INSERT,"Subject")

#Bindings
from_add.bind("<FocusIn>", lambda event: clear_placeholder(event, from_add, "Your Email Address"))
from_add.bind("<FocusOut>", lambda event: placeholder(event, from_add, "Your Email Address"))
from_add.bind("<Tab>", lambda event: tab_focus(event, to_add))
to_add.bind("<FocusIn>", lambda event: clear_placeholder(event, to_add, "Recipient"))
to_add.bind("<FocusOut>", lambda event: placeholder(event, to_add, "Recipient"))
to_add.bind("<Tab>", lambda event: tab_focus(event, header))
header.bind("<FocusIn>", lambda event: clear_placeholder(event, header, "Subject"))
header.bind("<FocusOut>", lambda event: placeholder(event, header, "Subject"))
header.bind("<Tab>", lambda event: tab_focus(event, main))
main.bind("<Tab>", lambda event: tab_focus(event, send))

#Packing
user_message.pack()
from_add.pack()
to_add.pack()
header.pack()
main.pack()
photo_bar.pack()
send.pack()

#Misc/Main
root.title("Cardy - A Postcard Sender")
root.mainloop()
