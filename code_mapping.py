class CodeMapping:

    def __init__(self,code) -> None:
        
        if isinstance(code, int):
            code = code
            
        elif isinstance(code, str):
            code = int(code)
        
        else:
            ...
        
        self.code_0_5 = code & 0x3f
        self.code_6_11 = (code >> 6) & 0x3f
        self.code_0_11 = code & 0xfff
        self.code_12_15 = (code >> 12) & 0xf 
        self.code_16_20 = (code >> 16) & 0x1f
        self.code_21_25 = (code >> 21) & 0x1f
        self.code_26_zf = (code >> 26) & 1
        self.code_27_zf = (code >> 27) & 1
        self.code_28_zf = (code >> 28) & 1
        self.code_29_zf = (code >> 29) & 1
        self.code_30_zf = (code >> 30) & 1
        self.code_31_zf = (code >> 31) & 1
        self.code_26_31 = (code >> 26) & 0x3f
        self.code_12_25 = (code >> 12) & 0x3fff
        self.code_26_30 = (code >> 26) & 0x1f
        self.code_7_12 = (code >> 7) & 0x3f