import string
import random


## characters to generate password from
characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

def generate_random_password():
	length = 8

	random.shuffle(characters)
	

	password = []
	for i in range(length):
		password.append(random.choice(characters))


	random.shuffle(password)

	## converting the list to string
	## printing the list
    
	slug = "".join(password)



## invoking the function
generate_random_password()