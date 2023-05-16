from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from enum import Enum
import blockchain as bc
from pow import powBlock
import hashlib as hash
import json
from constants import HASHPOOL_MINIMUM_TRUST, INITIAL_HASHPOOL_TRUST, INITIAL_WALLET_TRUST

wallet_PKs = [
    "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r",
    "16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe",
    "16rCmCmbuWDhPjWTrpQGaU3EPdZF7MTdUk",
    "3Cbq7aT1tY8kMxWLbitaG7yT6bPbKChq64",
    "3Nxwenay9Z8Lc9JBiywExpnEFiLp6Afp8v",
    "5Cbq7aT1tY8kMxWLbitaG7yT6bPbKChq64"
]



class powHistoryBlock(powBlock):
    def assignNonceRanges(self, pool_wallets, rangePerWallet):
        nonceRangePerWallet = {}
        endOfRange = 0
        finalIndex = 0

        assignmentNonce = self.nonce
        

        for i, wallet in enumerate(list(pool_wallets)):
            endOfRange = assignmentNonce+((i+1)*rangePerWallet)
            finalIndex = i
            nonceRangePerWallet[wallet] = (self.nonce+(i*rangePerWallet), (self.nonce+((i+1)*rangePerWallet)))
        assignmentNonce = (assignmentNonce+((i)*rangePerWallet))

        return nonceRangePerWallet, endOfRange

    def mine_work(self, pool_wallets):
        numberOfWallets = len(list(pool_wallets))
        rangePerWallet = 3
        nonceRangePerWallet, endOfRange = self.assignNonceRanges(pool_wallets, rangePerWallet)

        #Ideally this portion of the code would be threaded and each wallet would indiviually provide their own work simultaneously
        while not(self.check_correct_hash()):
            self.nonce += 1
            blockInfo = self.getWorkEncodedBlockInfo()
            updateHash = self.hash(blockInfo)
            self.blockHash = updateHash
            if self.nonce > endOfRange:
                nonceRangePerWallet, endOfRange = self.assignNonceRanges(pool_wallets, rangePerWallet)
        self.timestamp = datetime.now()

        self.workPerformed = (self.nonce // (numberOfWallets)) + (self.nonce % rangePerWallet)
        #print(workPerformed)

        for wallet, (start, stop) in nonceRangePerWallet.items():
            if self.nonce >= start and self.nonce <= stop:
                print(f"Successful Wallet: {wallet}")
                return wallet#, workPerformed
                


        

    def mine_trust(self):
        raise NotImplementedError("No Code")
    
    def check_correct_hash(self):
        if (self.blockHash[:5] == "00000"):
            return True
        return False
        
    
    #Timestamp should not be considered when mining a block so I left it out of the encoded block info
    def getWorkEncodedBlockInfo(self):
        info = {"index": self.index, "tx": self.txData, "nonce": self.nonce, "previous_hash": self.prevHash}
        encoded = json.dumps(info).encode()
        return encoded


class hashPool():
    def __init__(self, chainObject):
        self.pools = {}
        self.minimumTrust = HASHPOOL_MINIMUM_TRUST
        self.chainObject = chainObject
    
    def getPool(self, chain_index, pool_index):
        return self.pools[chain_index][pool_index]

    def create_hashPool(self, chainIndex, pool_index):
        if chainIndex not in self.pools:
            self.pools[chainIndex] = {}
        if pool_index in self.pools[chainIndex]:
            print(f"Pool index {pool_index} not available")
            return None

        self.pools[chainIndex][pool_index] = {}
    
    def join_hashPool(self, chainIndex, pool_index, wallet):
        walletTrust = self.chainObject.walletTrustScores[chainIndex][wallet]

        if chainIndex in self.pools and pool_index in self.pools[chainIndex]:
            if wallet in self.pools[chainIndex][pool_index]:
                print(f"{wallet[:3]}...{wallet[-3:]} already in pool {pool_index}")
            else:
                if walletTrust >= self.minimumTrust:
                    self.pools[chainIndex][pool_index][wallet] = INITIAL_HASHPOOL_TRUST
        
        
class powHistoryChain(bc.Blockchain):
    def __init__(self):
        super().__init__()
        self.walletTrustScores = {}
        self.onChainPoolManager = hashPool(self)
        self.chainType = "POWH"
        #self.json_init(self.chainType)
    
    def initializeWalletScores(self, chain_index, wallets):
        if chain_index not in self.walletTrustScores:
            self.walletTrustScores[chain_index] = {}

        for wallet in wallets:
            self.walletTrustScores[chain_index][wallet] = INITIAL_WALLET_TRUST
        
        print(self.walletTrustScores)

    def create_block(self, chain_index, tx):

        if chain_index not in self.chains:
            self.chains[chain_index] = []
            
        index = len(self.chains[chain_index])

        previous_hash = (self.chains[chain_index][-1]).blockHash if index > 0 else "0x00"
        newBlock = powHistoryBlock(index, tx, previous_hash)
        
        successfullWallet = newBlock.mine_work(self.walletTrustScores[chain_index])

        self.improveWalletTrust(chain_index, successfullWallet, newBlock)
        
        print(self.walletTrustScores[chain_index])

        updatedChain = self.chains[chain_index] + [newBlock]
        
        self.chains[chain_index] = updatedChain


    def improveWalletTrust(self, chain_index, wallet, block):
        workDoneByWallet = block.workPerformed
        workDoneTotal = block.nonce

        workPercentage = (workDoneByWallet / workDoneTotal)
        if wallet in self.walletTrustScores[chain_index]:
            currentTrust = self.walletTrustScores[chain_index][wallet]
            self.walletTrustScores[chain_index][wallet] += (currentTrust*workPercentage) * .3 




chainIndex = 0 
poolIndex = 11337


chains = powHistoryChain()
chains.initializeWalletScores(chainIndex, wallet_PKs)


chains.onChainPoolManager.create_hashPool(chainIndex, poolIndex)
chains.onChainPoolManager.join_hashPool(chainIndex, poolIndex, wallet_PKs[0])
chains.create_block(chainIndex, "john -> jason: 2")
chains.create_block(chainIndex, "john -> jason: 4")
chains.create_block(chainIndex, "john -> jason: 1")
chains.create_block(chainIndex, "john -> jason: 3")
chains.create_block(chainIndex, "john -> jason: 9")
#print(chains.walletTrustScores[chainIndex])
#print(chains.onChainPoolManager.pools)

