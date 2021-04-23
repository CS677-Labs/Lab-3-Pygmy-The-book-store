# TODO - Read from config file and initialize these 2 arrays
catalog_server_URLS = []
order_server_URLS = []
indexOfNextServer = 0


def getCatalogServerURL():
    global indexOfNextServer
    catalog_server = catalog_server_URLS[indexOfNextServer]
    indexOfNextServer = (indexOfNextServer + 1) % len(catalog_server_URLS)
    return catalog_server


def getOrderServerURL():
    global indexOfNextServer
    order_server = order_server_URLS[indexOfNextServer]
    indexOfNextServer = (indexOfNextServer + 1) % len(order_server_URLS)
    return order_server
