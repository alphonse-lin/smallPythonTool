def uniqueCount(tcList):
    tcSet = set(tcList)
    itemList = []
    countList = []
    for item in tcSet:
        itemList.append(item)
        countList.append(tcList.count(item))

    return itemList, countList