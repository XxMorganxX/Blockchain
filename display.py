from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from blockchain import Blockchain
import constants
import json
import hashlib as hash
import time

dc = None

class displayChain:
    def __init__(self, chainType):
        # Default Start Up*
        self.window = Tk()
        self.window.title("Blockchain Visualized")
        #self.window.attributes("-fullscreen", True)
        # self.window.iconbitmap("icon.ico")
        self.window.geometry("1900x1250")
        self.chainType = chainType
        self.chainIndex = "0"
        self.setUp()
    
    def setUp(self):

        self.blockHistory = self.getBlocks()[self.chainType][self.chainIndex]

        self.blockFrame = LabelFrame(self.window)
        self.blockFrame.place(relx=0.0075, rely=0.1)
        sep = ttk.Separator(self.blockFrame, orient="horizontal")
        sep.place()


        #ChainType dropdown
        options = {"POW": "Proof-of-Work", "POS": "Proof-of-Stake"}

        self.click = StringVar()
        self.click.set(options[self.chainType])

        drop = OptionMenu(self.window, self.click, *options.values())
        drop.place(relx=0.75, rely=0)


        dropDownSubmit = Button(self.window, text="Done", command=self.changeChainType)
        dropDownSubmit.place(relx=0.79, rely=0.026)



        #Display Initial Blocks
        self.displayStartIndex = 0
        match (self.chainType):
            case "POW":
                self.blocksToDisplay = 7
            case "POS":
                self.blocksToDisplay = 3

        self.cutBlockHistory = list(self.blockHistory)[
            self.displayStartIndex : self.displayStartIndex + self.blocksToDisplay
        ]
        for i in self.cutBlockHistory:
            self.drawBlock(i)

        # Header
        header = Label(self.window, text=f"{self.chainType} Chain", font=("Helvetica 30 bold"))
        header.place(relx=0.425, rely=0)

        # Block Slider
        self.slider = Scale(
            self.window,
            length=600,
            from_=1,
            to=100,
            orient=HORIZONTAL,
            command=lambda val: self.adjustSlider(),
        )
        self.slider.place(relx=0.35, rely=0.35)

        # POW Hashing Display
        if self.chainType == "POW":
            
            self.hashNonce = 0
            self.hashString = "0x00"

            self.hashFrame = LabelFrame(self.window)
            self.hashFrame.place(relx=0.05, rely=0.5)

            sep = ttk.Separator(self.hashFrame, orient="horizontal")
            sep.place()

            hashingHeader = Label(self.hashFrame, text=f"SHA-256 Hashing", font=("Helvetica 22 bold underline"))
            hashingHeader.pack()

            data = Label(self.hashFrame, text=f"data:", font=("Helvetica 16"))
            data.pack(anchor=W)

            self.input = Entry(self.hashFrame, width=50, highlightbackground="blue")
            self.input.pack()
            
            self.nonceText = Label(self.hashFrame, text=f"nonce: {self.hashNonce}", font=("Helvetica 14"))
            self.nonceText.pack(anchor=W)
            self.resultantHash = Label(self.hashFrame, text=f"Hash: {self.hashString}", font=("Helvetica 14"))
            self.resultantHash.pack(anchor=W)

            mine = Button(
                self.hashFrame, text="          Mine          ", command=self.mineClick
            )
            reset = Button(
                self.hashFrame, text="          Reset          ", command=self.resetClick
            )
            mine.pack(side=LEFT)
            reset.pack(side=RIGHT)
        
        if self.chainType == "POS":
            self.stakerFrame = LabelFrame(self.window)
            self.stakerFrame.place(relx=0.05, rely=0.415)            

            sep = ttk.Separator(self.stakerFrame, orient="horizontal")
            sep.place()


            stakingHeader = Label(self.stakerFrame, text=f"Staker List", font=("Helvetica 22 bold underline"))
            stakingHeader.pack()

            stakingDescription = Label(self.stakerFrame, text=f"Minimum to enter stake pool: {constants.STAKING_MINMUM}", font=("Helvetica 12"))
            stakingDescription.pack()
            
            stakingDescription = Label(self.stakerFrame, text=f"( [address: amount staked] - chance of being a validator)", font=("Helvetica 9"))
            stakingDescription.pack()

            self.stakerBox = LabelFrame(self.stakerFrame)
            self.stakerBox.pack(side=LEFT, padx=(15,0))

            sep = ttk.Separator(self.stakerBox, orient="horizontal")
            sep.place()

            self.stakers = {}

            self.totalValidStaked = 0

            for blockInfo in self.blockHistory.values():
                tx = blockInfo["txData"]
                parsedTx = Blockchain.transactionParser(tx)
                if parsedTx[1] == "STAKE":
                    if parsedTx[0] not in self.stakers:
                        self.stakers[parsedTx[0]] = parsedTx[2]
                    elif parsedTx[0] in self.stakers:
                        newStakeAmount = int(self.stakers[parsedTx[0]]) + int(parsedTx[2])
                        self.stakers[parsedTx[0]] = str(newStakeAmount)
            
            for staker, stakedAmount in self.stakers.items():
                stakedAmount = int(stakedAmount)
                if stakedAmount > constants.STAKING_MINMUM:
                    self.totalValidStaked += stakedAmount

            # Stake Slider
            self.stakeSlider = Scale(
                self.stakerFrame,
                length=300,
                from_=1,
                to=100,
                orient=VERTICAL,
                command=lambda val: self.adjustStakeSlider(),
            )
            self.stakeSlider.pack(side=RIGHT)
            
            
            self.stakersStartIndex = 0
            self.stakersToDisplay = 8
            self.firstTimeToDisplay = True
            self.adjustStakeSlider()


        self.window.mainloop()

    def adjustStakeSlider(self):
        initalStartIndex = self.stakersStartIndex

        value = self.stakeSlider.get() if self.stakeSlider.get() != 100 else 99

        self.stakersStartIndex = int(
            int(value) * ((len(list(self.stakers)) / 100))
        )
        
        sorted_stakers = sorted(self.stakers.items(), key=lambda x: int(x[1]), reverse=True)

        sorted_stakers = dict(sorted_stakers)

        cutStakersList = []
        if initalStartIndex != self.stakersStartIndex or self.firstTimeToDisplay:
            if self.firstTimeToDisplay:
                self.firstTimeToDisplay = False

            cutStakersList= list(sorted_stakers)[
                self.stakersStartIndex: self.stakersStartIndex + self.stakersToDisplay
            ]

            for widget in self.stakerBox.winfo_children():
                    widget.grid_forget()

            for i, staker in enumerate(cutStakersList):
                if i != 0 and int(sorted_stakers[cutStakersList[i-1]]) > constants.STAKING_MINMUM and int(sorted_stakers[cutStakersList[i]]) < constants.STAKING_MINMUM:
                    separator = Frame(self.stakerBox, height=1.5, bd=0, bg="Black", width=200)
                    separator.grid(column=0, row=i + 1)

                self.drawStaker(i, staker, sorted_stakers[staker])


    def drawStaker(self, i, k, v):
        if int(v) > constants.STAKING_MINMUM:        
            text = Label(self.stakerBox, text=f"[{k[:3]}...{k[-4:]}: {v}] - {round(((int(v)/self.totalValidStaked) *100),2)}%", font=("Helvetica 16"))
            text.grid(column=0, row=i + 1, padx=1)
        else:
            text = Label(self.stakerBox, text=f"[{k[:3]}...{k[-4:]}: {v}] - 0.0%", font=("Helvetica 16"))
            text.grid(column=0, row=i + 2, padx=1)



    def mineClick(self):
        if self.hashNonce == 0:
            while (self.hashString[:3] != "000"):
                self.hashNonce += 1
                blockInfo = self.getWorkEncodedBlockInfo(self.input.get())
                self.hashString = self.hash(blockInfo)
                self.nonceText.configure(text=f"nonce: {self.hashNonce}")
            self.resultantHash.configure(text=f"Hash: {self.hashString[:6]} ... {self.hashString[-6:]}")
        else:
            msg = messagebox.showerror("Error Silly Goose", "Reset the hashing first")

    def changeChainType(self):
        getSelected = self.click.get()
        typeReference = {"Proof-of-Work": "POW", "Proof-of-Stake": "POS"}
        newType = typeReference[getSelected]

        if newType != self.chainType:
            self.chainType = newType
            for widget in self.window.winfo_children():
                widget.destroy()
            self.setUp()
        self.click.set(getSelected)

        

    def resetClick(self):
        self.hashNonce = 0
        self.hashString = "0x00"
        self.nonceText.configure(text=f"nonce: {self.hashNonce}")
        self.resultantHash.configure(text=f"Hash: {self.hashString}")

    def hash(self, blockInfo):
        return hash.sha256(blockInfo).hexdigest()
    
    def getWorkEncodedBlockInfo(self, input):
        info = {"data": input, "nonce": self.hashNonce}
        encoded = json.dumps(info).encode()
        return encoded


    def adjustSlider(self):
        initalStartIndex = self.displayStartIndex

        value = self.slider.get() if self.slider.get() != 100 else 99

        self.displayStartIndex = int(
            int(value) * ((len(list(self.blockHistory)) / 100))
        )

        cutBlockHistory = list(self.blockHistory)[
            self.displayStartIndex : self.displayStartIndex + self.blocksToDisplay
        ]

        if initalStartIndex != self.displayStartIndex:
            for widget in self.blockFrame.winfo_children():
                widget.grid_forget()

            for i in cutBlockHistory:
                self.drawBlock(i)

    def drawBlock(self, blockIndex):
        blockInfo = self.blockHistory[str(blockIndex)]

        if "index" in blockInfo:
            blockInfo.pop("index")

        blockContainer = LabelFrame(self.blockFrame)
        blockContainer.grid(column=blockIndex, row=0, rowspan=5, padx=15, pady=20)

        sep = ttk.Separator(blockContainer, orient="horizontal")
        sep.grid()

        index_text = Label(
            blockContainer, text=f"Block # {blockIndex}", font=("Helvetica 24 bold")
        )
        index_text.grid(column=0, row=0, padx=2)

        for i, (key, value) in enumerate(blockInfo.items()):
            keyLabel = key
            valueLabel = value
            match key.lower():
                case "txdata":
                    keyLabel = "transaction"
                case "prevhash":
                    keyLabel = "previous_hash"
                    if len(value) > 10:
                        valueLabel = value[:3] + "..." + value[-4:]
                case "blockhash":
                    keyLabel = "block_hash"
                    if len(value) > 10:
                        valueLabel = value[:3] + "..." + value[-4:]
                case "approver":
                    if value[:3] == "0x0":
                        valueLabel = "approved by chain"
            keyLabel = keyLabel.upper()

            if not(self.chainType == "POS" and key == "nonce"):
                text = Label(blockContainer, text=f"{keyLabel}: {valueLabel}", font=("Helvetica 14"))
                text.grid(column=0, row=i + 1, padx=2)

    def getBlocks(self):
        try:
            with open("blocks.json", "r") as f:
                blockData = json.load(f)
            return blockData
        except:
            print("Error Getting Scores")
            return []
            


dc = displayChain("POS")