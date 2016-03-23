import urllib2
import json
from py2neo import Graph, Path

def saveToFIle(filename,query):
	fd=open(filename,'w')
	fd.write(query)
	fd.close()

#CYPHER requires keys to not have quotes around
#It filters out fields that don't have values
ignore=["ImageURL","ProductBonuses","ProductThumbnailUrl","Keywords"] 
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

def getListOf(url,key1,key2):
	store_ids=[]
	content = json.loads(urllib2.urlopen(url).read())
	for store in content[key1]:
		store_ids.append(store[key2])
	return store_ids



postalCode="H3A0B9"
closest_stores="http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetClosestStoresByPostalCode?orgCode=7778&bannerCode=23798&countryCode=CA&postalCode="+postalCode+"&culture=en"
stores = createQuery(closest_stores,"Stores","Store",0,'e')
saveToFIle("stores.txt",stores)
store_ids=getListOf(closest_stores,"Stores","StoreId")

published=""
pub_ids=[]
counter = 0
c = 102
for sid in store_ids:
	pub_url = "http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId="+sid
	published = published+createQuery(pub_url,"Publications","Publication",counter,str(unichr(c)))+","
	pub_ids=pub_ids+getListOf(pub_url,"Publications","PubId")
	c=c+1
	counter=counter+1

saveToFIle("publications.txt",published)

counter = 0
products=""
for pubId in pub_ids:
	prod_url="http://eflyer.metro.ca/MTR/MTR/fr/"+pubId+"/Product/ListAllProducts"
	products=products+createQuery(prod_url,"Products","Product",counter,str(unichr(c)))+","
	c=c+1
	counter = counter + 1

saveToFIle("products.txt",products)

#we need to use store ids to request data for publications
getPublicationsById = "http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId=5bbefd7f-3ebf-463a-8849-bf8c43959d52"
#http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId=store_id

#we need to use publication id for products
getProducts="http://eflyer.metro.ca/MTR/MTR/fr/dff75410-c7c1-486a-a32d-24688ac85c10/Product/ListAllProducts"
#saveToFIle("products.txt",createQuery(getProducts,"Products","Product"))
#http://eflyer.metro.ca/MTR/MTR/fr/publicationId/Product/ListAllProducts