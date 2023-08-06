# Turkish Full Name Generator
### Installation 
`pip install turkishfullnamegenerator`

### Usage
    import turkishfullname 
    fullname=turkishfullname.generate_name("erkek")
	print(fullname) #return str
    turkishfullname.generate_names("kadin") #return list of str
	
#### generate_name(gender)
Gender must be kadin,kadın,woman,erkek,man.
#### generate_names(gender,howmany)
howmany is positive integer. Gender is same as generate_name's gender.