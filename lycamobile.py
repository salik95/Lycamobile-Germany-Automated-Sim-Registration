from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import csv
import datetime
import os, sys

def func (username, password, pukcode, iccid, title, first_name, last_name, email, dob, phone_number, country, post_code, city_name, street_name, house_number, document_issuing_authority, document_id_number, file_name):

	# Standard wait time for any element to load
	STANDARD_WAIT_TIME = 60
	# Setting the option to run the web (Chrome) browser headless i.e. without the GUI window
	options = Options()
	options.headless = True
	options.add_argument("--no-sandbox") # bypass OS security model
	options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems

	driver = webdriver.Chrome(chrome_options=options)

	# Website URL
	driver.get("https://pos.lycamobile.de/Registration/Registration.aspx?lang=EN")
	# Input username
	driver.find_element_by_id("UserName").send_keys(username)
	# Input password
	driver.find_element_by_id("Password").send_keys(password)
	# Pressing Return button to enter the credentials to login
	driver.find_element_by_id("Password").send_keys(Keys.RETURN)
	# Contingency wait
	time.sleep(1)

	# Login the system with credentials logic
	load_timestamp = datetime.datetime.now()
	login_status = "None"
	while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
		try:
			if driver.find_element_by_id("updateProgress").get_attribute("aria-hidden") == "true":
				try:
					# Return on the error text on login failed
					return driver.find_element_by_id("FailureText").text
					login_status = "Failed"
				except:
					print("Credentials Passed")
					login_status = "Passed"
				break
			print("loading")
		except:
			print("Credentials Passed")
			break

	# If continously loading for more than 60 seconds, return timeout with login credentials failed message
	if login_status == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
		return "Server timeout on passing login credentials, try again!"
	# Click on sim registration button
	driver.execute_script("return SetRedirectUrl('../Registration/Registration.aspx?lang=EN');")
	driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$lnkSubMenuItem','');")

	# Loading time for the form to appear for pukcode and iccid
	load_timestamp = datetime.datetime.now()
	form_status = "None"
	while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
		try:
			# Switching the control to the details form (iframe)
			driver.switch_to_frame(driver.find_element_by_css_selector("body iframe"))
			form_status = "Avaialable"
			break
		except:
			print("Waiting for the form to load!")
			continue

	# Return with message of server timeout on getting pukcode iccid registration form
	if form_status == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
		return "Server timeout on Sim Registration form, try again!"

	# Selecting the radion button for entering pukcode
	pukcode_radio = driver.find_element_by_xpath('//input[@value="PUKCODE"]')
	driver.execute_script("arguments[0].click();", pukcode_radio)

	# Pukcode and ICCID input form values
	driver.find_element_by_id("PUKCODE").send_keys(pukcode)
	driver.find_element_by_id("ICCID").send_keys(iccid)
	step1_next = driver.find_element_by_css_selector("div.stepy-navigator a.button-next.btn-primary")
	driver.execute_script("arguments[0].click();", step1_next)

	# Loading time for pukcode and iccid acceptance
	load_timestamp = datetime.datetime.now()
	pukcode_validation = "None"
	while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
		if driver.find_element_by_id("GERForm-head-1").get_attribute("class") == "stepy-visited stepy-active":
		# If the step1 is checked marked that means pukcode and iccid has been validated and system has moved to step2
			pukcode_validation = "Passed"
			break
		elif driver.find_element_by_id("step1Msg").text != '':
		# Return with error message if pukcode and iccid is not passed
			time.sleep(3)
			return driver.find_element_by_id("step1Msg").text
			# pukcode_validation = "Failed"
			# break
		else:
			print("Waiting for Pukcode to be accepted")

	# Return with error message server timeout if pukcode and iccid validation keep on loading for more than 60 seconds
	if pukcode_validation == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
		return "Server timeout on Pukcode validation, try again!"

	try:
		# Start inputing the personal details of the sim holder
		title_select = select = Select(driver.find_element_by_id('Title')) 
		title_select.select_by_value(title)
	except:
		return "Invalid person title, please try again with valid title (Mr, Miss, Ms, Mrs, Sir, Dr, Prof)"

	driver.find_element_by_id("FirstName").send_keys(first_name)

	driver.find_element_by_id("LastName").send_keys(last_name)

	driver.find_element_by_id("EmailID").send_keys(email)

	# Input date of birth in format DD/MM/YYYY
	driver.execute_script("document.getElementById('DateOfBirth').setAttribute('value','" + str(dob) + "')")

	driver.find_element_by_id("OtherContact").send_keys(phone_number)

	driver.find_element_by_id("CommAddress_Country").clear()
	driver.find_element_by_id("CommAddress_Country").send_keys(country)

	driver.find_element_by_id("CommAddress_PostCode").send_keys(post_code)
	driver.find_element_by_id("CommAddress_PostCode").send_keys(Keys.RETURN)

	# Loading time for cities list to load for the given country and postcode
	load_timestamp = datetime.datetime.now()
	postalcode_validation = "None"
	while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
		if driver.find_element_by_id("NoRecord").text == "City load successfully,Please select the City Dropdown":
			# Right postal code has been selected
			postalcode_validation = "Passed"
			break
		elif driver.find_element_by_id("NoRecord").text == 'No Records Found':
			# Return with error message of invalid post code if received post code is not correct
			return "Invalid Postal Code, please try with a valid Postal Code"
		else:
			print("Waiting for Postal Code to be accepted")

	# Return with error message server timeout if postal code validation keep on loading for more than 60 seconds
	if postalcode_validation == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
		return "Server timeout on Postal Code validation, try again!"

	# Confirming to popup of right postal code and resulting in loading list of cities
	driver.find_element_by_id("btnFailedCancel").send_keys(Keys.RETURN)

	# Input city from the dropdown list
	city_select = select = Select(driver.find_element_by_id('CommAddress_ddCityLocality')) 
	try:
		city_select.select_by_value(city_name)
	except:
		# Return with error message of invalid city name if received city name is not correct
		return "Invalid City Name, please try with a valid City Name"

	# Loading time of street address for the selected city name but if not available then skip this step
	load_timestamp = datetime.datetime.now()
	street_name_availability = "None"
	while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
		if driver.find_element_by_id("NoRecord").text == "Street load successfully,Please select the Street Dropdown":
			# Streets list available for the selected city name
			street_name_availability = "Available"
			break
		elif driver.find_element_by_id("NoRecord").text == 'No Records Found':
			# Streets list not available for the selected city name
			street_name_availability = "Not Available"
			break
		else:
			print("Waiting for streets to appear!")

	if street_name_availability == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
		# Return with error message server timeout if street records keep on loading for more than 60 seconds
		return "Server timeout on street records, try again!"
	elif street_name_availability == "Available":
		# If street names are available then input the received street name in function arguments
		driver.find_element_by_id("btnFailedCancel").send_keys(Keys.RETURN)
		street_select = Select(driver.find_element_by_id('CommAddress_ddStreet')) 
		try:
			street_select.select_by_value(street_name)
		except:
			# Return with error message of invalid street name if street names were available but right street name wasn't received
			return "Invalid Street Name, please try with a valid Street Name"
		
		# Loading time for house number selection if the street name was available and validated
		load_timestamp = datetime.datetime.now()
		house_number_availability = "None"
		while (datetime.datetime.now() - load_timestamp).seconds < STANDARD_WAIT_TIME:
			if driver.find_element_by_id("NoRecord").text == "House Number Premise load successfully,Please select the House Number Dropdown":
				# If house numbers were available and the list is loaded successfully
				house_number_availability = "Available"
				break
			elif driver.find_element_by_id("NoRecord").text == 'No Records Found':
				# If no records for house number was available 
				house_number_availability = "Not Available"
				break
			else:
				print("Waiting for house numbers to appear!")
		try:
			# Confirm the popup of house number being availabel
			driver.find_element_by_id("btnFailedCancel").send_keys(Keys.RETURN)
		except:
			pass

		if house_number_availability == "None" and (datetime.datetime.now() - load_timestamp).seconds >= STANDARD_WAIT_TIME:
			# If house number was either not available or the popup never showed and the house number list was directly populated. In either case it will keep on loading for more than 60 seconds and leading to this condition being true
			if len(driver.find_element_by_id("CommAddress_ddHouseNo").find_elements_by_css_selector("option")) > 1:
				# Checking if in case house number was actually available but system never showed the popup though the list for house number dropdown was populated hence the list of options will always be greater than 1
				house_number_availability = "Available"
			else:
				# If the list wasn't greater than 1 and hence the house number availability was None that means it took more than 60 seconds to load hence return with server timeout error message
				return "Server timeout on house number records, try again!"
	else:
		# If the street address was valid but system do not have any registered house number against the street so the system will ask to enter custom house number
		house_number_availability = "Not Available"
		# Clicking on the popup to confirm house numbers not available message
		driver.find_element_by_id("btnFailedCancel").send_keys(Keys.RETURN)


	if house_number_availability == "Available":
		# If house numbers were available and the list is populated successfully with more than 1 record naturally
		house_select = Select(driver.find_element_by_id('CommAddress_ddHouseNo'))
		try:
			# Select the house number from dropdown list
			house_select.select_by_value(house_number)
		except:
			# Return with error message for invalid house number
			return "Invalid House Number, please try with a valid House Number"
	else:
		# If house number list wasn't populated hence the user will have to enter custom house number
		if len("12") > 2:
			# If the length of house number is greater than 2 digits then return with error message because the system doesn't support house numbers having more that 2 digits
			return "Invalid House Number, please try with a valid House Number"
		# Input the house number
		driver.find_element_by_id("CommAddress_HouseNo").send_keys(house_number)

	# Always select the type of document to be passport [HARD CODED IN THE TRY BLOCK]
	# The script do not support any other type of document to be uploaded - [can be introduced in next phase]
	document_type = Select(driver.find_element_by_id('IDOption'))
	try:
		document_type.select_by_value('Passport')
	except:
		# Return with error message for invalid document type (that can be passport, driving license, etc.)
		return "Invalid Document Type, please try with a valid Document Type"

	driver.find_element_by_id("IDNumber").send_keys(document_id_number)
	driver.find_element_by_id("IssuingAuthority").send_keys(document_issuing_authority)
	# os.getcwd() gets current working directory path added with filename of the document to be uploaded along with the extension
	driver.find_element_by_id("Upload1").send_keys(os.getcwd() + file_name)

	# Click check terms and condition and other check box
	driver.execute_script("arguments[0].click();",driver.find_element_by_id("chkDocument"))
	driver.execute_script("arguments[0].click();",driver.find_element_by_id("chkTermsCondition"))

	# Click on next button to go on previewing the form
	confirm_step1 = driver.find_element_by_css_selector("fieldset[id='GERForm-step-1'] div.stepy-navigator a.button-next.btn-primary")
	driver.execute_script("arguments[0].click();", confirm_step1)

	# Contingency pause
	time.sleep(3)
	
	# Confirm the data and submit
	confirm = driver.find_element_by_css_selector("fieldset[id='GERForm-step-2'] div.stepy-navigator button.stepy-finish.confirm-success")
	driver.execute_script("arguments[0].click();", confirm)

	time.sleep(30)
	# Return whatever text displays at the end
	return driver.find_element_by_id("message").text

if __name__ == '__main__':
	print(func(*sys.argv[1:]))