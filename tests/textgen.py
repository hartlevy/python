#!/usr/bin/python

import random
import re

wtype=1
nptype=2
vptype=3
stype=4

class Fragment:		
	def __init__(self,text="",kind=0):
		self.text=text
		self.kind=kind
		self.length=0
		if(text==""):
			print "New empty fragment"
		else:
			print "New fragment: ", self.text
		
	def __str__(self):
		return self.text

class Word(Fragment):
	wlist=("")
	nwords=len(wlist);
	def __init__(self,text="",num=0):
		self.text=text
		self.kind=1
		if num<0 or num>=1:
			num=0
		if self.text=="":
			self.text=self.wlist[int(self.nwords*num)]

			

class Npart(Fragment):
	def __init__(self,text="",length=0):
		self.text=text
		self.kind=2
		self.length=length

	def gen(self):

		self.length=1
		self.adj=""
		while (random.random()) < 0.5*5**(-self.length+1):
			self.adj+=" "+str(Adjective("",random.random()))			
			self.length += 1

		self.noun=str(Noun("",random.random()))
		self.text=self.adj+" "+self.noun
		
		self.det=str(Determ("",random.random()))
		if(re.match(r'[aeiouAEIOU]',self.text[1]) and self.det=="a"):
			self.det="an"
		self.text=" "+self.det+self.text
		self.length+=1		


class Vpart(Fragment):
	def __init__(self,text="",length=0):
		self.text=text
		self.kind=3
		self.length=length

	def gen(self):
		self.verb=Verb("",random.random())
		self.length+=1
		self.np=Npart()
		self.np.gen()
		self.length+=self.np.length
		self.text=self.verb.text+self.np.text

class Sentence(Fragment):
	def __init__(self,text=""):
		self.text=text
		self.kind=4
		if(text==""):
			self.np=Npart()
			self.np.gen()
			self.vp=Vpart()
			self.vp.gen()
			self.text=self.np.text+ " "+self.vp.text+'.'
			self.length=self.np.length+self.vp.length
			print "Sentence: ", self.text

	def gen(self):
		self.np=Npart()
		self.np.gen()
		self.vp=Vpart()
		self.vp.gen()
		self.text=self.np.text+ " "+self.vp.text+'.'
		self.length=self.np.length+self.vp.length
		print "Sentence: ", self.text
		
	def printme(self):
		print "Sentence: ", self.text

class Determ(Word):	
	wlist=('a','the')
	nwords=len(wlist);
class Verb(Word):
	wlist=('ate','ran','met','saw','held','broke','smelled','found','married')
	nwords=len(wlist);
class Noun(Word):
	wlist=('dog','hotdog','chicken','couch','remote control','refrigerator','clock')
	nwords=len(wlist);
class Conjunction(Word):
	wlist=('')
	nwords=len(wlist);
class Adjective(Word):
	wlist=('smelly','smart','happy','evil','ugly','sad','broken','late','uncomfortable')
	nwords=len(wlist);
class Adverb(Word):
	wlist=('')
	nwords=len(wlist);
