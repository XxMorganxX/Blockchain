from datetime import datetime
from enum import Enum
import blockchain as bc
import hashlib as hash
import json, constants

class powBlock(bc.Block):
    def mine(self):
        while not(self.check_correct_hash()):
            self.nonce += 1
            blockInfo = self.getWorkEncodedBlockInfo()
            updateHash = self.hash(blockInfo)
            self.blockHash = updateHash
        self.timestamp = datetime.now()
    
    def check_correct_hash(self):
        if (self.blockHash[:5] == "00000"):
            return True
        return False
    
    #Timestamp should not be considered when mining a block so I left it out of the encoded block info
    def getWorkEncodedBlockInfo(self):
        info = {"index": self.index, "tx": self.txData, "nonce": self.nonce, "previous_hash": self.prevHash}
        encoded = json.dumps(info).encode()
        return encoded

class powChain(bc.Blockchain):
    
    def __init__(self):
        super(powChain, self).__init__()
        self.chainType = "POW"
        self.json_init(self.chainType)


    def create_block(self, chainIndex, tx):

        if chainIndex not in self.chains:
            self.chains[chainIndex] = []
            
        index = len(self.chains[chainIndex])

        previous_hash = (self.chains[chainIndex][-1]).blockHash if index > 0 else constants.DEFAULT_ADDRESS
        newBlock = powBlock(index, tx, previous_hash)
        newBlock.mine()

        updatedChain = self.chains[chainIndex] + [newBlock]
        
        self.chains[chainIndex] = updatedChain
        print(newBlock)





#chain = powChain()
#chain.create_block(0, "john -> jason: 3")
#chain.create_block(0, "john -> jason: 2")
#print(chain.transactionParser("john -> jason: 2"))
#print(chain.getAllTransactions(0))

#chain.transcribe_all_blocks(0, chain.chainType)

#print(chain.chains)
#chain.update_current_chain()