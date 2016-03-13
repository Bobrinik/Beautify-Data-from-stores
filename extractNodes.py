import urllib2
import json
from py2neo import Graph, Path

def saveToFIle(filename,query):
	fd=open(filename,'w')
	fd.write(query)
	fd.close()

#CYPHER requires keys to not have quotes around
#It filters out fields that don't have values 
def formQuery(st):
	query=''
	for s in st.keys():
		clean=json.dumps(s).replace('"','')
		if len(json.dumps(st[(s)]))==2 or json.dumps(st[(s)]) in 'null':
			continue
		query=query+clean+":"+json.dumps(st[(s)])+","
	return "{"+query.strip(',')+"}"

def createQuery(url_link,key_to_get,label):
	content = json.loads(urllib2.urlopen(url_link).read())
	i=0
	cypher_create="CREATE "
	query_body=""
	for store in content[key_to_get]:
		 query_body=query_body+"CREATE (e"+str(i)+":"+label+" "+formQuery(store)+")\n"
		 i=i+1
	return query_body 


postalCode="H3A0B9"
closest_stores="http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetClosestStoresByPostalCode?orgCode=7778&bannerCode=23798&countryCode=CA&postalCode="+postalCode+"&culture=en"
#stores = createQuery(closest_stores,"Stores","Store")
#saveToFIle("stores.txt",stores)

#we need to use store ids to request data for publications
getPublicationsById = "http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId=5bbefd7f-3ebf-463a-8849-bf8c43959d52"
#http://eflyer.metro.ca/MTR/MTR/fr/Landing/GetPublicationsByStoreId?storeId=store_id

#we need to use publication id for products
getProducts="http://eflyer.metro.ca/MTR/MTR/fr/dff75410-c7c1-486a-a32d-24688ac85c10/Product/ListAllProducts"
saveToFIle("products.txt",createQuery(getProducts,"Products","Product"))
#http://eflyer.metro.ca/MTR/MTR/fr/publicationId/Product/ListAllProducts