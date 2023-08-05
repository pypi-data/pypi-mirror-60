import requests
print ('Hello This is SAE News')
url = 'http://updateinspyre.surge.sh/hello.py'
r = requests.get(url)
f = open('updater.py','wb')
f.write(r.content)
f.close()
print ('Downloaded')

