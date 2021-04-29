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
        found=False
        # Todo: Have a max tries and fail after that.
        while not found:
            catalog_server = Server.catalog_servers_urls[indexOfNextServer]   
            indexOfNextServer = (indexOfNextServer + 1) % len(Server.catalog_servers_urls)   
            found=catalog_server[1]
            
    return catalog_server[0]

def getOrderServerURL() :
    global indexOfNextServer
    global lock
    with lock:
        found=False
        # Todo: Have a max tries and fail after that.
        while not found:
            order_server = Server.order_servers_urls[indexOfNextServer]
            found=order_server[1] and Server.catalog_servers_urls[indexOfNextServer][1]
            indexOfNextServer = (indexOfNextServer + 1) % len(Server.order_servers_urls)
            
    return order_server[0]
