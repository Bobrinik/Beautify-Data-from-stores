import urllib2
import json
from py2neo import Graph, Path
import sys
from selenium import webdriver

def saveToFIle(filename,query):
	fd=open(filename,'w')
	fd.write(query)
	fd.close()

#CYPHER requires keys to not have quotes around
#It filters out fields that don't have values
ignore=["ImageURL","ProductBonuses","Keywords"] 
def formQuery(st):
	query=''
	for s in st.keys():
		clean=json.dumps(s).replace('"','')
		if s in ignore: #extract separetly
			continue
		if len(json.dumps(st[(s)]))==2 or json.dumps(st[(s)]) in 'null':
			continue
		if s in "Url":
			query = query+clean+":"+'"'+json.dumps(st[(s)]).split("=")[1]+"," #"Url": "/MTR/MTR/fr/463cf50a-81e3-4026-b242-26c8a1564748/Page?storeId=3ba677d9-c7fe-4aea-ab18-e871085f5b69"
			continue
		query=query+clean+":"+json.dumps(st[(s)])+","
	return "{"+query.strip(',')+"}"

def createQuery(url_link,key_to_get,label,i,var):
	content = json.loads(urllib2.urlopen(url_link).read())
	cypher_create="CREATE "
	query_body=""
	for store in content[key_to_get]:
		 query_body=query_body+"CREATE ("+var+str(i)+":"+label+" "+formQuery(store)+")\n"
		 i=i+1
	return query_body 

def simpleCreateQuery(url_link,label,i,var):
	content = json.loads(urllib2.urlopen(url_link).read())
	cypher_create="CREATE "
	query_body=""
	query_body=query_body+"CREATE ("+var+str(i)+":"+label+" "+formQuery(content)+")\n"
	return query_body	

#http://eflyer.metro.ca/MTR/MTR/fr/Text?province=QC
def get_store_ids(url,store_name):
	driver=webdriver.Firefox()
	driver.get(url)
	store_ids =""
	i=1
	while True:
		try:
			city_link = driver.find_element_by_xpath("id('CityList')/a["+str(i)+"]")
			city_link.click()
			j=1
			while True:
				try:
					store_link = driver.find_element_by_xpath("id('StoreList')/a["+str(j)+"]")
					store_ids=store_ids+store_link.get_attribute('href').split("=")[1].strip()+","
					print store_link
					j=j+1
				except:
					driver.get("http://eflyer.metro.ca/MTR/MTR/fr/Text?province=QC")
					break
			i = i + 1
		except:
			break
	saveToFIle(store_name,store_ids.strip(","))


def get_store_ids2(url,store_name):
	driver=webdriver.Firefox()
	driver.get(url)
	store_ids =""
	i=1
	while True:
		try:
			city_link = driver.find_element_by_xpath("id('CityList')/a["+str(i)+"]")
			city_link.click()
			j=1
			while True:
				try:
					store_link = driver.current_url
					if "province" in store_link:

						try:
							link=driver.find_element_by_xpath("id('StoreList')/a["+str(j)+"]")
							store_ids=store_ids+link.get_attribute('href').split("=")[1].strip()+","
							j=j+1
						except:
							driver.get(url)
							break
					else:
						store_ids=store_ids+store_link.split("=")[1].split("&")[0]+","
						j=j+1
						driver.get(url)
						break
				except:
					driver.get(url)
					break
			i = i + 1
		except:
			break
	saveToFIle(store_name,store_ids.strip(","))


def getAllStoreNodes(store_ids,store="MTR"):
	if store in "SUPRC":
		sr_utl_info = "http://eflyer.metro.ca/SUPRC/SUPRC/fr/Publication/StoreInfo?storeId="
	else:
		sr_utl_info = "http://eflyer.metro.ca/MTR/MTR/fr/Publication/StoreInfo?storeId="
	i=0
	store_nodes=""
	for store_id in store_ids:				
		store_info = sr_utl_info + store_id
		print store_info
		store_nodes=store_nodes+simpleCreateQuery(store_info,"Store",i,'f')
		i=i+1
	saveToFIle("store_info_"+store,store_nodes+";")






def getListOf(url,key1,key2):
	store_ids=[]
	content = json.loads(urllib2.urlopen(url).read())
	for store in content[key1]:
		store_ids.append(store[key2])
	return store_ids

def load_storeids(store):
	fd = open(store,"r")
	data=fd.read()
	return data.split(",")



def getPublications(store_ids,store="MTR"):
	if store in "SUPRC":
		pub_url = "http://eflyer.metro.ca/SUPRC/SUPRC/fr/Landing/GetPublicationsByStoreId?storeId="
	else:
		pub_url = "http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId="

	published=""
	pub_ids=[]
	counter = 0
	c = 102
	for sid in store_ids:
		print pub_url+sid	
		published = published+createQuery(pub_url+sid,"Publications","Publication",counter,"a")
		pub_ids=pub_ids+getListOf(pub_url+sid,"Publications","PubId")
		c=c+1
		counter=counter+1

	result={}
	for pid in pub_ids:
		result[pid]=0
	saveToFIle("published_all_"+store,published+";")
	return result.keys()

def get_products(pub_ids,store="MTR"):
	c=102
	counter = 0
	products=""
	for pubId in pub_ids:
		prod_url=""
		if store in "MTR":
			prod_url="http://eflyer.metro.ca/MTR/MTR/fr/%s/Product/ListAllProducts" % pubId
		else:
			prod_url="http://eflyer.metro.ca/SUPRC/SUPRC/fr/%s/Product/ListAllProducts" % pubId
		print prod_url
		products=products+createQuery(prod_url,"Products","Product",counter,str(unichr(c)))
		c=c+1
		counter = counter + 1
	saveToFIle("products_"+store,products.strip(",")+";")



if __name__ == "__main__":

	if "-store_id" in sys.argv:
		if "MTR" in sys.argv:
			print "getting store_ids for Metro"
			get_store_ids("http://eflyer.metro.ca/MTR/MTR/fr/Text?province=QC","metro_ids")
		
		if "SUPRC" in sys.argv:
			print "getting store_ids for Super C"
			get_store_ids2("http://eflyer.metro.ca/SUPRC/SUPRC/fr/Text?province=QC","superc_ids")

	if "-load_pub" in sys.argv:
		if "MTR" in sys.argv:
			print "loading MTR store_ids"
			store_ids = load_storeids("metro_ids")
			unique_pub_ids = getPublications(store_ids)
			pub_ids = ','.join(unique_pub_ids)
			saveToFIle("unique_pub_ids_mtr",pub_ids)

		if "SUPRC" in sys.argv:
			print "loading SUPRC store_ids"
			store_ids = load_storeids("superc_ids")
			unique_pub_ids = getPublications(store_ids,"SUPRC")
			pub_ids = ','.join(unique_pub_ids)
			saveToFIle("unique_pub_ids_suprc",pub_ids)

	if "-load_store_info" in sys.argv:
		if "SUPRC" in sys.argv:
			store_ids = load_storeids("superc_ids")
			getAllStoreNodes(store_ids, "SUPRC")

		if "MTR" in sys.argv:
			store_ids = load_storeids("mtr_ids")
			getAllStoreNodes(store_ids, "MTR")

	if "-load_products" in sys.argv:
		if "SUPRC" in sys.argv:
			pub_ids = load_storeids("unique_pub_ids_suprc")
			get_products(pub_ids, "SUPRC")

		if "MTR" in sys.argv:
			pub_ids = load_storeids("unique_pub_ids_suprc")
			get_products(pub_ids, "MTR")
	else:
		print "No arguments where passed"
