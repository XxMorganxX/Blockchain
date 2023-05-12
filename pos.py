from datetime import datetime
import blockchain as bc
import hashlib as hash
import json
from math import fsum
from random import uniform
import constants

wallet_PK = [
    "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r",
    "16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe",
    "16rCmCmbuWDhPjWTrpQGaU3EPdZF7MTdUk",
    "3Cbq7aT1tY8kMxWLbitaG7yT6bPbKChq64",
    "3Nxwenay9Z8Lc9JBiywExpnEFiLp6Afp8v",
    "8ayWdjInbSd97aY7d9A09wD87ALkdwANdN",
    "Be0acA30e893fF717C1452431836aF78BB",
    "C20B73f39AC109e465291d25c560Ae9318",
]


class posBlock(bc.Block):
    def __init__(self, index, tx, walletApprover, previousHash):
        previousHash = previousHash or constants.DEFAULT_ADDRESS
        super(posBlock, self).__init__(index, tx, previousHash)
        self.approver = walletApprover

    def fix(self):
        blockInfo = self.getStakeEncodedBlockInfo()
        updatedHash = self.hash(blockInfo)
        self.blockHash = updatedHash
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"{self.index}, {self.timestamp}, {self.txData}, {self.approver}, {self.blockHash[:3]}...{self.blockHash[-4:]}, {self.prevHash[:3]}...{self.prevHash[-4:]}"

    def getStakeEncodedBlockInfo(self):
        info = {
            "index": self.index,
            "tx": self.txData,
            "approver": self.approver,
            "previous_hash": self.prevHash,
        }
        encoded = json.dumps(info).encode()
        return encoded


class posChain(bc.Blockchain):
    def __init__(self):
        super(posChain, self).__init__()
        self.stakers = {}
        self.json_init("POS")
        


    def chooseStaker(self, chainIndex):
        if chainIndex not in self.stakers:
            self.stakers[chainIndex] = {}

        possibleStakers = {}


        for staker, stakedAmount in self.stakers[chainIndex].items():
            if stakedAmount > constants.STAKING_MINMUM:
                possibleStakers[staker] = stakedAmount
        
        if len(list(possibleStakers)) == 0:
            print("Can not add block, no validators")
            return False
        
        #print(f"Possible Stakers: {possibleStakers}")
        
        
        weights = [0.0]
        for i, (_, v) in enumerate(possibleStakers.items()):
            weights.append(weights[-1] + v)
        
        rand = uniform(weights[0], weights[-1])
        for i, weight in enumerate(weights):
            if rand > weight and rand < weights[i + 1]:
                return list(possibleStakers)[i]
        

    def create_block(self, chainIndex, tx):
        if chainIndex not in self.chains:
            self.chains[chainIndex] = []

        index = len(self.chains[chainIndex])
        previous_hash = (self.chains[chainIndex][-1]).blockHash if index > 0 else constants.DEFAULT_ADDRESS
        approver = None

        sender, reciever = self.transactionParser(tx)[0], self.transactionParser(tx)[1]

        

        if reciever == "STAKE" or sender == "CHAIN":
            approver = constants.DEFAULT_ADDRESS
        else:
            approver = self.chooseStaker(chainIndex)

        if approver != False:
            newBlock = posBlock(index, tx, approver, previous_hash)
            newBlock.fix()

            updatedChain = self.chains[chainIndex] + [newBlock]

            self.chains[chainIndex] = updatedChain

        #print(self.chains[chainIndex])

    def stake(self, chainIndex, wallet, amount):

        if chainIndex not in self.stakers:
            self.stakers[chainIndex] = {}
        if wallet not in self.stakers[chainIndex]:
            self.stakers[chainIndex][wallet] = 0

        newStakeAmount = self.stakers[chainIndex][wallet] + amount
        if newStakeAmount < constants.STAKING_MINMUM:
            print(f"Wallet only enters the stake pool if its stake is more than {constants.STAKING_MINMUM}...")
            print(f"You have only staked {newStakeAmount}")
            pass

        allValues = self.getAllValues(chainIndex)


        if allValues[wallet] > amount:
            self.stakers[chainIndex][wallet] = newStakeAmount

            # Empty Approver
            self.create_block(chainIndex, f"{wallet} -> STAKE: {amount}")
        else:
            print("Insufficient funds to stake")


chain = posChain()
chain.create_block(0, f"CHAIN -> {wallet_PK[0]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[1]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[2]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[3]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[4]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[5]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[6]}: 100")
chain.create_block(0, f"CHAIN -> {wallet_PK[7]}: 100")
chain.create_block(0, f"{wallet_PK[5]} -> {wallet_PK[6]}: 5")
chain.stake(0, wallet_PK[0], 4)
chain.stake(0, wallet_PK[1], 5)
chain.stake(0, wallet_PK[1], 25)
chain.stake(0, wallet_PK[2], 31)
chain.stake(0, wallet_PK[3], 32)
chain.stake(0, wallet_PK[4], 33)
chain.stake(0, wallet_PK[5], 34)
chain.stake(0, wallet_PK[6], 35)
chain.stake(0, wallet_PK[7], 36)
chain.create_block(0, f"{wallet_PK[5]} -> {wallet_PK[6]}: 5")
chain.create_block(0, f"{wallet_PK[5]}-> {wallet_PK[7]}: 5")




#Make sure stakers percent chance of winning is displayed
chain.transcribe_all_blocks(0, "POS")