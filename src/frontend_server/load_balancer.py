from threading import Lock
lock = Lock()
indexOfNextServer = 0

class Server:
    catalog_servers_urls=[]
    order_servers_urls=[]
    frontend_servers_urls=[]

def getCatalogServerURL() :
    global indexOfNextServer
    global lock
    with lock:
        catalog_server = Server.catalog_servers_urls[indexOfNextServer]
        indexOfNextServer = (indexOfNextServer + 1) % len(Server.catalog_servers_urls)
    return catalog_server

def getOrderServerURL() :
    global indexOfNextServer
    global lock
    with lock:
        order_server = Server.order_servers_urls[indexOfNextServer]
        indexOfNextServer = (indexOfNextServer + 1) % len(Server.order_servers_urls)
    return order_server
