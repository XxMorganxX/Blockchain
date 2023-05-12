from datetime import datetime
import hashlib as hash
import json
import constants


class Block():

    def __init__(self, index, transactionData, previousHash = constants.DEFAULT_ADDRESS):
        self.index = index
        self.nonce = 0
        self.txData = transactionData
        self.blockHash = ""
        self.prevHash = previousHash
        self.timestamp = None


    def __repr__(self):
        return f"{self.index}, {self.timestamp}, {self.txData}, {self.nonce}, {self.blockHash[:3]}...{self.blockHash[-4:]}, {self.prevHash[:3]}...{self.prevHash[-4:]}"


    def print_timestamp(self):
        print(self.timestamp.strftime("%H:%M:%S"))


    @staticmethod   #Static method decorator used to called a function without needing an instance of the object
    def hash(blockInfo):
        return hash.sha256(blockInfo).hexdigest()
    

    def get_all_info(self):
        return self.__dict__
    
    

    

class Blockchain():

    def __init__(self):
        self.chains = {}
        self.currentChain = []
    

    def json_init(self, chainType):
        try:
            blockData = None
            with open("blocks.JSON", "r") as f:
                blockData = json.load(f)
            
            if chainType not in blockData:
                blockData[chainType] = {}
            
            with open("blocks.JSON", "w") as outfile:
                json_object = json.dumps(blockData, indent=1)
                outfile.write(json_object)
        except:
            print(f"Problem with {chainType} Json init")
    

    def update_current_chain(self):
        mostRecentTimestamp = datetime(2023, 1, 1, 1, 0, 0, 0)
        currentChainIndex = None

        for k, arr in self.chains.items():
            if arr[-1].timestamp != None and arr[-1].timestamp > mostRecentTimestamp:
                currentChainIndex = k
                mostRecentTimestamp = arr[-1].timestamp
        
        print(currentChainIndex)

    @staticmethod
    def transactionParser(tx):
        arrowIndex = tx.find("->")
        amountIndex = tx.find(":")
        sender = tx[:arrowIndex-1]
        reciever = tx[arrowIndex+3:amountIndex]
        amount = tx[amountIndex+2:]
        return (sender, reciever, amount)
        

    def getAllTransactions(self, chainIndex):
        if chainIndex not in self.chains:
            self.chains[chainIndex] = []

        transactions = []
        chain = self.chains[chainIndex]


        for block in chain:
            transactions.append(block.txData)
        
        return transactions
    

    def getAllValues(self, chainIndex):
        #iterate through a chain and return a dictionary with the amount each wallet or person earns
        transactions = self.getAllTransactions(chainIndex)
        values = {}

        for i, tx in enumerate(transactions):
            transactions[i] = self.transactionParser(tx)
        
        for tx in transactions:
            sender, reciever, amount = tx[0].strip(), tx[1].strip(), float(tx[2].strip())


            if sender not in values:
                values[sender] = -1 * amount
            else:
                values[sender] = values[sender] - amount

            if reciever not in values:
                values[reciever] = amount
            else:
                values[reciever] = values[reciever] + amount
            
            if "CHAIN" in values:
                del values["CHAIN"]

        
        return values


    def transcribe_all_blocks(self, chainIndex, chainType):
        transcribeChain = self.chains[chainIndex]
        #print(transcribeChain)
        transcribedBlocks = {str(chainIndex): {}}
        for block in transcribeChain:
            info = block.get_all_info()
            info["timestamp"] = str(info["timestamp"])
            transcribedBlocks[str(chainIndex)][str(block.index)] = {}
            transcribedBlocks[str(chainIndex)][str(block.index)] = info
        

        try:
            blockData = None
            with open("blocks.JSON", "r") as f:
                blockData = json.load(f)

            #print(blockData)

            if chainType in blockData:
                blockData[chainType] = transcribedBlocks
                #print(blockData)
            
            with open("blocks.JSON", "w") as outfile:
                json_object = json.dumps(blockData, indent=3)
                outfile.write(json_object)
        except:
            print("Couldn't write blocks to JSON - blockchain.py")


    def verify_valid_chain(self, chainIndex, chainType):
        if chainIndex not in self.chains:
            self.chains[chainIndex] = []

        blockIndex = 0
        previous_Hash = constants.DEFAULT_ADDRESS

        chain = self.chains[chainIndex]

        while blockIndex < len(chain):
            indexedBlock = chain[blockIndex]
            encodedBlockInfo = indexedBlock.getEncodedBlockInfo()
            decodedBlockInfo = eval(indexedBlock.getEncodedBlockInfo().decode())
            

            print(decodedBlockInfo, end="")
            
            
            if decodedBlockInfo["index"] != blockIndex:
                print("Invalid Index")
                return False

            if chainType == "POW":
                indexedBlockHash = Block.hash(encodedBlockInfo)
                if indexedBlock.blockHash != indexedBlockHash:
                    print(f"Invalid Hashing {indexedBlock.hash} != {indexedBlockHash}" )
                    return False
            
                if decodedBlockInfo["previous_hash"] != previous_Hash:
                    print("Invalid Previous Hashing")
                    return False


            blockIndex += 1
            print(f" {indexedBlock.blockHash}")
            previous_Hash = indexedBlock.blockHash

        return True
