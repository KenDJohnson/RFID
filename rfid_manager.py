#!/usr/bin/python2
# Ken Johnson
# 08/03/2014
#
# Utility for managing RFID Tags with the Parallax Inc. RFID
# Reader/Writer #28440 Revision A.
# Error descriptions taken from Parallax module datasheet
# 
# Licensed under MIT 2014
# 
import serial
import time
rfid = serial.Serial('/dev/ttyUSB0',9600,timeout=5)

# Command set for Parallax serial communication
read_code = '\x01'
write_code = '\x02'
login_code = '\x03'
set_pass_code = '\x04'
reset_code = '\x05'
read_legacy_code = '\x0F'

# Error codes
ok_1 = "No errors"
liw_2 = "Could not find listen window (LIW) from the tag"
nak_3 = """Received a No Acknowledge (NAK), possible communication error or
 invalid command/data"""
nak_oldpw_4 = """Received No Acknowledge (NAK) sending current password druing
              the RFID SetPass command, possible incorrect password"""
nak_newpw_5 = """Received No Acknowledge (NAK) sending the new password during" 
              the RFID SetPass command"""
liw_newpw_6 = """Could not find LIW from the tag after setting the new password
              during the RFID SetPass command"""
parity_7 = "Parity error when reading data from the tag"

last_read = ""

# Read the data stored in addr
def read():
	addr = raw_input("Address to read from: ")
	rfid.flush()
	rfid.write("!RW") # Send the listen command
	rfid.write(read_code) # Send the read code
	print "Hold tag to reader/writer, wait until LED is green."
	time.sleep(3)	
#	print chr(int(addr))
	rfid.write(chr(int(addr))) # Send the address to be read from
#	response = rfid.read(1) ## Used for debugging
#	print to_hex(response)
#	print
#	if(err_check(response)):
	if(err_check(rfid.read(1))): # Check for the response and if err_ok
		last_read = rfid.read(4) # Store the returned value for ASCII printing
		print to_hex(last_read) # Print out the data in hex

# Read data from @addr arg for use with mem_dump()
def read_addr(addr):
	rfid.write("!RW")
	rfid.write(read_code)
	rfid.write(addr)
	if(err_check(rfid.read(1))):
		print to_hex(rfid.read(4))


# Write @data to @addr in the EEPROM of the tag
def write():
	addr = raw_input("Address to write to: ")
	data = chr(int(raw_input("First byte to write (in DEC): ")))
	data += chr(int(raw_input("Second byte to write (in DEC): ")))
	data += chr(int(raw_input("Third byte to write (in DEC): ")))
	data += chr(int(raw_input("Fourth byte to write (in DEC): ")))
	
	addr = chr(int(addr))
#	data = chr(int(data))
	if len(data)>4:
		print "There are only 4 bytes to write to, try a smaller input"
		return -1
	else:
		rfid.flush()
		rfid.write("!RW") # Send listen command
		rfid.write(write_code) # Send write code
		rfid.write(addr) # Send address to write to
		rfid.write(data) # Send data to enter
		if(err_check(rfid.read(1))): # Check for errors
			print "Successfuly wrote %s to address %s" %(to_hex(data), to_hex(addr))

# Login to the tag
def login():
	passwd = raw_input("Enter the password for the tag: ") # Read in password
	while(len(passwd)>4): # Make sure password entered is only 4 bytes
		print "The password was too long. Try again..."
		passwd = raw_input("Enter the password for the tag: ")
	passwd = to_hex(passwd) # Convert passwd to hex 
    #####^^MIGHT NOT WORK^^ will return 0x format, need in char. Is this necessary?
	print "Logging in..."
	rfid.write("!RW") # Header
	rfid.write(login_code) # Login code
	rfid.write(passwd) # Send the password to be written to 0x00
	if(err_check(rfid.read(1))): # Check for errors and if all good print success
		print "Login successful"
	
def set_pass():
	tries = 0 # Number of times trying to reset password
	changed = False # bool for pass change success
	while(not changed and tries < 3):
		tries += 1 # Increment the number of tries
        # Read in the old_password
		old_passwd = raw_input("Enter the current password for the tag: ") 
        # Read in the new password
		new_passwd = raw_input("Enter the new password: ") 
        # Check password for errors
		if(new_passwd == raw_input("Re-enter the new password: ")):
			rfid.write("!RW")
			rfid.write(set_pass_code)
			rfid.write(old_passwd)
			rfid.write(new_passwd)
			changed = rfid.read(1)
			if(changed):
				print "Changed the password"
			elif(not changed and tries > 3):
				print "Password unchanged, try again (%i/3)"%tries
			else:
				print "Password unchanged, try 3 of 3\nExiting..."

# Print out the data read from the tag in HEX
def to_hex(string):
	hex_string = ""
	for i in string:
		hex_string += "0x%s\t" % (i.encode('hex'))
	return hex_string


# Check the error code returned from the module and print corresponding
# error
def err_check(code):
	if code == '\x01' :
		return True
	elif code == '\x02' :
		print "Error code 0x02: %s."%liw_2
		return False
	elif code == '\x03' :
		print "Error code 0x03: %s."%nak_3
		return False
	elif code == '\x04' :
		print "Error code 0x04: %s."%nak_oldpw_4
		return False
	elif code == '\x05' :
		print "Error code 0x05: %s."%nak_newpw_5
		return False
	elif code == '\x06' :
		print "Error code 0x06: %s."%liw_newpw_6
		return False
	elif code == '\x07' :
		print "Error code 0x07: %s."%parity_7
		return False
	else:
		print "Something went horribly wrong"
		return False
	return False

def mem_dump():
	print "Place the card by the reader/writer, wait for LED to turn red, then green"
	time.sleep(3)
	for i in range(0x00, 0x22):
		print "%x\t"%i,
		read_addr(chr(i))
		print "-------------------------------------"

def ascii_last():
	print str(last_read)

def print_help():
	print "\nCommand\t\tDescription"
	print "read\t\tRead from the EEPROM of the tag"
	print "write\t\tWrite to the EEPROM of the tag"
	print "login\t\tLogin to the tag if it is password protected"
	print "dump\t\tDump data from all 33 address of EEPROM"
	print "print\t\tPrint out the last read data in ASCII"
	print "exit\t\tExit out of the program"
	print "h\t\tPrint this help menu\n"


def __main__():
	prompt = "Command (press h for a list of commands): "
	cmd = ""
	while(cmd != "exit"):
		cmd = raw_input(prompt)
		if (cmd == "read"):
			read()
		elif (cmd == "write"):
			write()
		elif (cmd == "login"):
			login()
		elif (cmd == "dump"):
			mem_dump()
		elif (cmd == "h"):
			print_help()	
		elif (cmd == "print"):
			ascii_last()
		else:
			print "Command not recognized, type h for help"


print "Ken Johnson's RFID Read/Write Utility, for use with PARALLAX #28440"
__main__()	
