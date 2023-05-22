from code_mapping import CodeMapping
from loguru import logger
import math
"""
    probably need unicorn to load so and find specific offset.
""" 

def dispatch(VM_REGS):
    ...

def deref(variable):
    ...

def ref(addr):
    
    # designed for return a certain value from ram addr
    ...

def get_variable(variable_name):
    ...

def negate():
    ...
    
def dispatch():
    ...

def write_mem(a,b):
    ...

def HIDWORD(num):
    # consider num as 64 bit reg
    if num & 0xffffffff00000000 > 0:
        return num >> 32
    else:
        return 0

def LODWORD(num):
    ...

def SLOWORD(num):
    ...

def ROR(num, offset):
    ...

def complement(num):
    bit_length = len(bin(num))-2
    #print(bit_length)
    extend_exp= math.ceil(math.log(bit_length, 2))
    extend_size = 2 ** extend_exp
    origin = (1<<extend_size) - num 
    if origin < num:
        return -origin
    else:
        return num
    #print(extend_size)

MEMORY_EFCC0 = []
# VM_REGS could be inherited from last vm caller, but it includes so many ram based structures, 
# need to simplfy a liitle bit.
# there is some 16bit signed num in calculation, need to extended to 32bit unsigned numbers.

def Vm(code_bytearray, a2, a3, a4, a5, q0=None, VM_REGS=None):

    """
        a5: a5[0] -> vm_jmp_caller call()
            a5[1] -> caller function sp qword/ set virtual registers base offset
            a5[2] -> unknown
    """
    base_addr = 0

    VM_REGS = {
        "m0" : a5[1],   # m0 , looks like vm caller's lr
        "m1" : code_bytearray, # vm_code_ptr, point to the first instruction to be executed, will not change.
        "m2": 0,
        "m3": 0,
        "m4": 0, # vm execution status | enum {0,1,2,3} # m0 - 0x20
        "m5": 0,
        "m6": 0,
        "m7":  a5[2], 
        "m8": 0,
        "m9": 0, # a5[1] - 0x148 & 0xFFFFFFFFFFFFFFF0, # m0 - 82 => m41 & 0xFFFFFFFFFFFFFFF0 # if stacked, then m41 should be last vm call's m1, well actually aligned m1
        "m10": 0, 
        "m11": 0, 
        "m12": 0,
        "m13": 0,
        "m14": 0,
        "m15": 0,
        "m16": 0,
        "m17": 0,
        "m18": 0,
        "m19": 0,
        "m20": 0,
        "m21": 0,
        "m22": 0,
        "m23": 0, #VR0
        "m24": 0,
        "m25": 0,
        "m26": 0,
        "m27": 0,
        "m28": 0,
        "m29": 0,
        "m30": 0,
        "m31": a5[0],     # vm inputs 
        "m32": a4, 
        "m33": a3,  # v137
        "m34": a2,  # v139
        "m35": 0,
        "m36": 0, # v138 # fpr handle result 
        "m37": 0,
        "m38": 0, #VR15
        "m39": code_bytearray, # VREGS_BASE m0-78  #pc #stack SP
    } # m7 - m38 can be modified

    vm_code = None # 32bit int
    vm_handle_jmp = a5[0]
    cursor_end = a5[2] # v8
    
    code_bytearray_base_addr = 0 #  address
    code_bytearray_size = 1
    code_bytearray_idx_addr =0 
    code_bytearray_idx = 0
    
    vm_code_ptr = 0

    if cursor_end != code_bytearray_idx_addr:
        v138 = a5[1] - 0x120    
    else:
        return code_bytearray
    
    while code_bytearray_idx_addr != cursor_end:

        # setting vm exec state    
        vm_exec_state = VM_REGS["m4"]
        if vm_exec_state == 2:
            VM_REGS["m4"] = 3
            vm_exec_state = 3

        vm_code = code_bytearray[code_bytearray_idx_addr: code_bytearray_size]
        vm_code = 0x257F26A
        cm = CodeMapping(vm_code) # easy for representation
        logger.info(f"{hex(vm_code)} comes to branch:{cm.code_0_5}")

        
        op1_base_ptr = 39-cm.code_16_20
        op2_base_ptr = 39-cm.code_21_25
        """
            # these register has different uses
        """

        if cm.code_0_5 in (0,1,2,9,10,15,16,17,23,26,28,29,30,33,35,36,46,48,55,56,57,59,61):
            logger.info(f"Branch {cm.code_0_5} Direct Dispatch")
            dispatch()
            break

        elif cm.code_0_5 in (3,4,5,6):
            #v_reg_6_11x26_31x12_15 = VM_REGS[op2_base_ptr-1] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            dispatch()

        elif cm.code_0_5 == 7:
            # arithmetic instructions
            match cm.code_0_11:
                case 455: # 0x1c7 -> 000111 000111
                    m5 = VM_REGS['m5']
                    m6 = VM_REGS['m6']
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                    res = m6 | (m5 << 0x20) + reg_1 * reg_2
                    VM_REGS['m6'] = res
                    VM_REGS['m5'] = HIDWORD(res) #for carry bits?

                case 519: # 0x207 -> 001000 000111
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] * VM_REGS[f"m{op2_base_ptr-1}"]

                case 1287:# 0x507 -> 010100 000111
                    m5 = VM_REGS['m5']
                    m6 = VM_REGS['m6']
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                    res = m6 | (m5 << 0x20) - reg_1 * reg_2
                    VM_REGS['m6'] = res
                    VM_REGS['m5'] = HIDWORD(res) #for carry bits?

                case 2183:# 0x887 -> 100010 000111
                    m5 = VM_REGS['m5']
                    m6 = VM_REGS['m6']
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                    res = m6 | (m5 << 0x20) + reg_1 * reg_2
                    VM_REGS['m6'] = res
                    VM_REGS['m5'] = HIDWORD(res) #for carry bits?

                case 4039:# 0xfc7 -> 111111 000111
                    m5 = VM_REGS['m5']
                    m6 = VM_REGS['m6']
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                    res = m6 | (m5 << 0x20) - reg_1 * reg_2
                    VM_REGS['m6'] = res
                    VM_REGS['m5'] = HIDWORD(res) #for carry bits?

                case _:
                    ...
            dispatch()
        
        elif cm.code_0_5 == 8:
            #L113
            """
                ram operation
            """
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            v57 = ((reg_2 + (cm.code_26_31<<6+cm.code_6_11)) << 3) & 0x18 # get 24bit
            v58 = 0xFFFFFFFF << -v57 # negate v57 
            v52 = reg_1 & (0xFFFFFFFF << -v57) | ((reg_2_offset & 0xFFFFFFFFFFFFFFFC).value() >> v57)
            VM_REGS[f"m{op1_base_ptr-1}"] = v52
            dispatch()
            
        elif cm.code_0_5 == 11:
            #TODO: routine check here
            # reg_1_offset 16bit 0-65535 + VM_REGS[x] in x8, 64bit 
            """
                ram operation
                instruction -> ?
            """
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            v1 = reg_2_offset & 0xFFFFFFFFFFFFFFFC # should be a ram address and with out last 2 bit , looks like align operation
            av1 = v1.value() # not implemented, according to disassembly should also be an address
            v2 = (0xFFFFFFFF >> (0xF8 * (reg_2_offset & 0b11))) # that last 2 bit -> v2 should be 0 or ffffffff
            v3 = VM_REGS[f"m{op1_base_ptr-2}"] << ((reg_2_offset & 0b11) << 3)
            av1 = v1 & v2 | v3 # write 2 ram
            dispatch()

        elif cm.code_0_5 in (12,13):
            """
                pc operation
            """
            # looks like move pc to next instruction
            if vm_exec_state > 0:
                dispatch()

            v1 = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            if (vm_code & 0x3e) != 0xc:
                dispatch()
            
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            v47 = vm_code_ptr + v1 + 4
            if cm.code_0_5 == 12:
                if reg_2 < 1: # signed compare, convert modification need
                    VM_REGS["m3"] = v47
                else:
                    VM_REGS["m3"] = vm_code_ptr + 8
                    VM_REGS["m4"] = 2
            else:
                if reg_2 <= 0:
                    VM_REGS["m3"] = v47
                    VM_REGS["m4"] = 1
                else:
                    VM_REGS["m3"] = v47
                    VM_REGS["m4"] = 2
            
            dispatch()

        elif cm.code_0_5 == 14: 
            """
                str reg1, [reg_2, offset]
            """
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            tmp = reg_2 + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            VM_REGS[f"m{op1_base_ptr-1}"] = tmp.value()
            dispatch()

        elif cm.code_0_5 == 17:
            reg_2_offset =  VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            dispatch()
        
        elif cm.code_0_5 == 18:
            #tmp = base_addr + 0x28850 # tmp <- vm_code_12_15
            if vm_exec_state > 0: dispatch()
            vm_code_12_25x26_31x6_11_lsl_2 = (cm.code_12_25 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            VM_REGS["m3"] = VM_REGS["m1"] + vm_code_12_25x26_31x6_11_lsl_2
            VM_REGS["m4"] = 2
            VM_REGS["m7"] = vm_code_ptr + 8
            VM_REGS["m2"] = vm_code_ptr + 8
            dispatch()
        
        elif cm.code_0_5 == 19:
            # L615, yet not fully understand , need trace and examples
            # tmp = base_addr + 0x28850 # tmp <- vm_code_12_15
            # write_mem((op2_base_ptr+8*tmp).value(), cm.code_16_20)
            # after re-decompile, this pass is only dispatch()
            dispatch()
        
        elif cm.code_0_5 in (20,21):
            """
                ldr r1, [r2, #offset]
            """
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            VM_REGS[f"m{op1_base_ptr-1}"]  = reg_2_offset.value() 
        
        elif cm.code_0_5 == 22:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
            v56 = (reg_1 & 0xFFFFFFFFFFFFFFF8).value() # deref
            v57 = ((reg_2 + cm.code_6_11 + cm.code_26_31 << 6) << 3) & 0x38 # possible overflow here
            v58 = 0xFFFFFFFFFFFFFFFF << negate(v57)
            VM_REGS[f"m{op1_base_ptr-1}"] =  reg_1 & v58 | (v56 >> v57)
            dispatch()
        
        elif cm.code_0_5 == 24:
            """
            # add r2, r2, #offset
            # mov r1, r2
            """
            VM_REGS[f"m{op1_base_ptr-1}"] = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            dispatch()
    
        elif cm.code_0_5 == 25:
            """
                write to mem according to register
            """
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            v67 = reg_2_offset & 0xFFFFFFFFFFFFFFF8
            fpr_call_buf = v67.value() & (0xFFFFFFFFFFFFFFFF >> negate(reg_2_offset << 3) & 0x38) | (reg_1 << (reg_2_offset << 3) & 0x38); # wandering is this value 0?
            write_mem(v67.value(), fpr_call_buf)
            dispatch()

        elif cm.code_0_5 == 27:
            """
                ldr r1, [r2, #offset]
            """
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            VM_REGS[f"m{op1_base_ptr-1}"] = reg_2_offset.value()
            ...
        
        elif cm.code_0_5 == 31:
            if vm_exec_state > 0: dispatch()
            tmp = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            v47 = vm_code_ptr + tmp + 4
            if reg_1 != reg_2:
                # l171
                VM_REGS["m3"] = vm_code_ptr + tmp + 4
                VM_REGS["m4"] = 2
                
            else:
                # l215
                VM_REGS["m3"] = vm_code_ptr + 8
                VM_REGS["m4"] = 2
            
            dispatch()                

        elif cm.code_0_5 == 32:
            if vm_exec_state > 0: dispatch()
            tmp = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            if reg_2 <= 0:
                # l215
                VM_REGS["m3"] = vm_code_ptr + 8
                VM_REGS["m4"] = 2
                
            else:
                # l171
                VM_REGS["m3"] = vm_code_ptr + tmp + 4
                VM_REGS["m4"] = 2
            
            dispatch()
        
        elif cm.code_0_5 == 34:
            # write 2 mem
            # str reg1, [reg2, #offset]
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + (cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12)
            print(f"m{op2_base_ptr-1}",f"m{op1_base_ptr-1}", hex(reg_2_offset))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            write_mem(reg_2_offset.value(), reg_1)
            dispatch()
        
        # elif cm.code_0_5 == 35:
        #     #reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
        #     dispatch()
        
        elif cm.code_0_5 == 37:
            # opposite to cm.code_0_5 == 31
            if vm_exec_state > 0: dispatch()
            tmp_2 = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"] 
            if reg_1 == reg_2:
                # l171
                VM_REGS["m3"] = vm_code_ptr + tmp_2 + 4
                VM_REGS["m4"] = 2
            else:
                # l215
                VM_REGS["m3"] = vm_code_ptr + 8
                VM_REGS["m4"] = 2
            dispatch()
        
        elif cm.code_0_5 == 38:
            if vm_exec_state > 0: dispatch()
            tmp = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"] 
            if reg_2 >= 1:
                # l217
                VM_REGS["m3"] = vm_code_ptr + 8
                VM_REGS["m4"] = 1
            else:
                # l220
                VM_REGS["m3"] = vm_code_ptr + tmp + 4
                VM_REGS["m4"] = 2
            dispatch()
        
        elif cm.code_0_5 == 39: # 0b100111
            # flow control
            tmp = cm.code_16_20 << 16 + cm.code_0_5 
            
            if cm.code_16_20 not in (4,5,9,12,13,17,21,26):
                dispatch()
            
            if vm_exec_state > 0:
                dispatch()
            
            tmp_2 = (cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"] 
            if cm.code_16_20 == 26:
                # l404
                if reg_2 & 0x8000000000000000 == 0: # i guess this should be always 0
                    # l269
                    VM_REGS['m3'] = vm_code_ptr + 8
                    VM_REGS['m4'] = 2
                else:
                    # l428
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
            
            elif cm.code_16_20 == 21:
                if reg_2 & 0x8000000000000000 != 0:
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 2
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                    
            elif cm.code_16_20 == 17:
                if reg_2 & 0x8000000000000000 == 0: 
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 1
                    VM_REGS['m7'] = vm_code_ptr + 8
                    VM_REGS['m2'] = vm_code_ptr + 8
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8
                    VM_REGS['m2'] = vm_code_ptr + 8

            
            elif cm.code_16_20 == 13:
                if reg_2 & 0x8000000000000000 != 0:
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 1
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
            
            elif cm.code_16_20 == 12:
                if reg_2 & 0x8000000000000000 == 0:
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8 
                    VM_REGS['m2'] = vm_code_ptr + 8 
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8 
                    VM_REGS['m2'] = vm_code_ptr + 8
                    

            elif cm.code_16_20 == 9:
                if reg_2 & 0x8000000000000000 == 0: 
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 2
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                
            elif cm.code_16_20 == 5:
                flag = 0x1f
                if reg_2 & 0x8000000000000000 != 0:  
                    VM_REGS['m3'] = vm_code_ptr + 8
                    VM_REGS['m4'] = 1
                    VM_REGS['m7'] = vm_code_ptr + 8 
                    VM_REGS['m2'] = vm_code_ptr + 8 
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8
                    VM_REGS['m2'] = vm_code_ptr + 8


            elif cm.code_16_20 == 4:
                if reg_2 & 0x8000000000000000 != 0:  
                    VM_REGS['m3'] = vm_code_ptr + 8 
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8
                    VM_REGS['m2'] = vm_code_ptr + 8
                else:
                    VM_REGS['m3'] = vm_code_ptr + tmp_2 + 4
                    VM_REGS['m4'] = 2
                    VM_REGS['m7'] = vm_code_ptr + 8
                    VM_REGS['m2'] = vm_code_ptr + 8

            dispatch()

        elif cm.code_0_5 == 40:
            """
                ldr r1, [r2, #offset]
            """
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            write_mem(reg_2_offset.value(), reg_1)
            dispatch()

        elif cm.code_0_5 == 41:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            VM_REGS[f"m{op1_base_ptr-1}"] =  reg_2_offset
            dispatch()

        elif cm.code_0_5 == 42:
            # REG BETWEEN ARITHMATIC OPERATIONS
            print(cm.code_6_11)
            logger.info("Branch 42:")

            match cm.code_6_11:
                case 0:
                    # LSL VRm, VRn
                    # MOV VRd, VRm
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] << VM_REGS[f"m{op2_base_ptr-1}"]
                case 1:
                    # SUBS VRd, VRm, VRn
                    VM_REGS[f"m{38-cm.code_12_15}"] = SEXT(VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"])  # concealed LODWORD() and sign extension
                case 2:
                    # LSR VRm, #imm 
                    # MOV VRd, VRm
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] >> cm.code_26_30
                case 3:
                    # AND VRd, VRm, VRn
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] & VM_REGS[f"m{op2_base_ptr-1}"]
                case 4:
                    # NOP
                    ...
                case 5:
                    # LSL VRm, #imm(unsigned)
                    # MOV VRd. VRm
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] << (cm.code_26_30 | 0x20)
                case 6:
                    # mul VXd, VWm, VWn
                    # mov VR6, VXd
                    # lsr VXd, 0x20
                    # mov VR5, VXd
                    res = VM_REGS[f"m{op1_base_ptr-1}"] * VM_REGS[f"m{op2_base_ptr-1}"]
                    VM_REGS['m5'] = res >> 0x20
                    VM_REGS['m6'] = res & 0xffffffff
                case 7:
                    # SUB VRd, VRm, VRn (TODO: negative value representation)
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"]
                case 8:
                    # UDIV or SDIV?
                    res = VM_REGS[f"m{op2_base_ptr-1}"] / VM_REGS[f"m{op1_base_ptr-1}"]
                    rem = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"] * res
                    VM_REGS[f"m5"] = rem
                    VM_REGS[f"m6"] = res
                case 9:
                    # ADD VRd, VRm, VRn (TODO: overflow representation)
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"] + VM_REGS[f"m{op1_base_ptr-1}"]
                case 10:
                    # NOR VRd, VRm, Vrn (TODO: register based operation)
                    VM_REGS[f"m{38-cm.code_12_15}"] = negate(VM_REGS[f"m{op1_base_ptr-1}"] | VM_REGS[f"m{op2_base_ptr-1}"])
                case 11:
                    # LSL(bits croped)
                    VM_REGS[f"m{38-cm.code_12_15}"] = (VM_REGS[f"m{op1_base_ptr-1}"] << VM_REGS[f"m{op2_base_ptr-1}"]) & 0xffffffff
                case 12:
                    # NOP
                    ...
                case 13:
                    # SDIV?
                    res = VM_REGS[f"m{op2_base_ptr-1}"] / VM_REGS[f"m{op1_base_ptr-1}"]
                    rem = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"] * res
                    VM_REGS['m5'] = rem & 0xffffffff
                    VM_REGS['m6'] = res & 0xffffffff
                case 14:
                    # ROR
                    if cm.code_26 == 1:
                        VM_REGS[f"m{38-cm.code_12_15}"] = ((VM_REGS[f"m{op1_base_ptr-1}"] << (0x20 - VM_REGS[f"m{op2_base_ptr-1}"])) | (VM_REGS[f"m{op1_base_ptr-1}"] >> VM_REGS[f"m{op2_base_ptr-1}"])) & 0xffffffff
                    else:
                        VM_REGS[f"m{38-cm.code_12_15}"] = (VM_REGS[f"m{op1_base_ptr-1}"] >> VM_REGS[f"m{op2_base_ptr-1}"]) & 0xffffffff
                case 15:
                    # ADDS VRd, VRm, VRn
                    VM_REGS[f"m{38-cm.code_12_15}"] = (VM_REGS[f"m{op1_base_ptr-1}"] + VM_REGS[f"m{op2_base_ptr-1}"]) & 0xffffffff
                case 16:
                    # LSL #imm
                    # using qword to store, so probably store in 2 register
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] << cm.code_26_30
                case 17:
                    # NOP
                    ...
                case 18:
                    # ?
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS["m6"]
                case 19:
                    # ?DIV ? 
                    res = VM_REGS[f"m{op2_base_ptr-1}"] / (VM_REGS[f"m{op1_base_ptr-1}"] & 0xffffffff)
                    rem = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"] * res
                    VM_REGS[f"m5"] = rem & 0xffffffff
                    VM_REGS[f"m6"] = res & 0xffffffff
                case 20:
                    # NOP
                    ...
                case 21:
                    # ADDS
                    VM_REGS[f"m{38-cm.code_12_15}"] = (VM_REGS[f"m{op1_base_ptr-1}"] + VM_REGS[f"m{op2_base_ptr-1}"]) & 0xffffffff
                case 22:
                    # LSR
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] >> (cm.code_26_30|0x20)
                case 23:
                    # NOP
                    ...
                case 24:
                    # SPECIAL, looks like read next inst and setting m3 m4
                    if vm_exec_state == 0:
                        VM_REGS[f"m4"] = 2
                        VM_REGS[f"m3"] = VM_REGS[f"m{op2_base_ptr-1}"]
                        vm_code_ptr = VM_REGS["m39"] + sizeof(INST)
                        VM_REGS["m39"] = vm_code_ptr
                    else:
                        #NOP
                        ...
                case 25:
                    # NOP
                    ...
                case 26:
                    # ?
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS["m6"]
                case 27:
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] ^ VM_REGS[f"m{op2_base_ptr-1}"] 
                case 28:
                    # store in qword, is this signed unrelevant?
                    res = VM_REGS[f"m{op2_base_ptr-1}"] / VM_REGS[f"m{op1_base_ptr-1}"]
                    rem = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"] * res
                    VM_REGS[f"m5"] = rem 
                    VM_REGS[f"m6"] = res
                case 29:
                    # CMP VRn, VRm (Alike, not really is this instruction)
                    VM_REGS[f"m{39-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"] < VM_REGS[f"m{op1_base_ptr-1}"]
                case 30:
                    # controvertible
                    VM_REGS[f"m{39-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"] < VM_REGS[f"m{op1_base_ptr-1}"]
                case 31:
                    # NOP
                    ...
                case 32:
                    # NOP
                    ...
                case 33:
                    # NOP
                    ...
                case 34:
                    logger.info("\tsub6_11:34")
                    if vm_exec_state > 0: dispatch()
                    VM_REGS['m3'] = VM_REGS[f"m{op2_base_ptr-1}"]
                    VM_REGS['m4'] = 2
                    if cm.code_12_15 > 0:
                        VM_REGS[f"m{39-cm.code_12_15}"] = vm_code_ptr + 8
                        VM_REGS["m2"] = vm_code_ptr + 8
                case 35:
                    logger.info("\tsub6_11:35")
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    reg_2 = VM_REGS[f"m{op2_base_ptr-1}"] 
                    tmp = reg_1 * reg_2 
                    VM_REGS['m5'] = tmp
                    VM_REGS['m6'] = tmp >> 0x20
                case 36:
                    if (vm_code >> 21) & 1 == 1:
                        # l371
                        VM_REGS[f'{38-cm.code_12_15}'] = ROR(VM_REGS[f"m{op1_base_ptr-1}"], cm.code_26_30)
                    elif (vm_code >> 21) & 1 == 0:
                        VM_REGS[f'{38-cm.code_12_15}'] = VM_REGS[f"m{op1_base_ptr-1}"] >> cm.code_26_30
                case 37:
                    # NOP
                    ...
                case 38:
                    # NOP
                    ...
                case 39:
                    tmp = VM_REGS[f"m{op1_base_ptr-1}"] * VM_REGS[f"m{op2_base_ptr-1}"]
                    VM_REGS["m5"] = tmp >> 0x40
                    VM_REGS["m6"] = tmp
                case 40:
                    if (vm_code >> 21) & 1 == 1:
                        VM_REGS[f'{38-cm.code_12_15}'] = ROR(VM_REGS[f'm{op1_base_ptr}'], (cm.code_26_30|0x20))
                    else:
                        # not sure
                        ...
                case 41:
                    # NOP
                    ...
                case 42:
                    # ROR8 imm # TODO: this implementation is wrong 
                    code_21 = cm.code_21_25 & 1
                    if code_21 == 1:
                        VM_REGS[f"m{38-cm.code_12_15}"] = ((VM_REGS[f"m{op1_base_ptr-1}"] << (0x20 - VM_REGS[f"m{op2_base_ptr-1}"])) | (VM_REGS[f"m{op1_base_ptr-1}"] >> VM_REGS[f"m{op2_base_ptr-1}"])) & 0xffffffff
                    else:
                        VM_REGS[f"m{38-cm.code_12_15}"] = (VM_REGS[f"m{op1_base_ptr-1}"] >> VM_REGS[f"m{op2_base_ptr-1}"]) & 0xffffffff
                case 43:
                    # ROR8 imm # TODO
                    ...
                
                case 44:
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] >> cm.code_26_30
                
                case 45:
                    #NOP
                    ...
                
                case 46:
                    VM_REGS['m6'] = VM_REGS[f"m{op2_base_ptr-1}"]
                
                case 47:
                    #NOP
                    ...
                
                case 48:
                    if VM_REGS[f"m{op1_base_ptr-1}"] == 0:
                        VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"]
                    else:
                        # NOP
                        ...
                case 49:
                    if VM_REGS[f"m{op1_base_ptr-1}"] != 0:
                        VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"]
                    else:
                        # NOP
                        ...
                case 50:
                    VM_REGS['m5'] = VM_REGS[f"m{op2_base_ptr-1}"]
                case 51:
                    # NOP
                    ...
                case 52:
                    # MULS? 
                    tmp = (VM_REGS[f"m{op2_base_ptr-1}"] * VM_REGS[f"m{op1_base_ptr-1}"])
                    VM_REGS["m6"] = tmp
                    VM_REGS["m5"] = tmp >> 0x40
                case 53:
                    # ORR VRd, VRm, VRn
                    VM_REGS[f"m{38-cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] | VM_REGS[f"m{op2_base_ptr-1}"]
                case 54:
                    # ADD EXT 
                    VM_REGS[f"m{op2_base_ptr - cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] + VM_REGS[f"m{op2_base_ptr-1}"]
                case 55:
                    # SUB EXT
                    VM_REGS[f"m{op2_base_ptr - cm.code_12_15}"] = VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"]
                case 56:
                    # SUBS EXT
                    VM_REGS[f"m{op2_base_ptr - cm.code_12_15}"] = SXTW(VM_REGS[f"m{op2_base_ptr-1}"] - VM_REGS[f"m{op1_base_ptr-1}"])
                case 57:
                    # NOP
                    ...
                case 58:
                    # NOP
                    ...
                case 59:
                    # LSR reg EXT
                    VM_REGS[f"m{op2_base_ptr - cm.code_12_15}"] = VM_REGS[f"m{op1_base_ptr-1}"] >> VM_REGS[f"m{op2_base_ptr-1}"] 
                
                case 60:
                    # ROR reg EXT
                    VM_REGS[f"m{op2_base_ptr - cm.code_12_15}"] = ...
                
                case 61:
                    #NOP
                    ...
                
                case 62:
                    #NOP
                    ...
                
                case 63:
                    #NOP
                    ...
                

            dispatch()
                    
        
        elif cm.code_0_5 == 43:
            if vm_exec_state > 0:
                dispatch()
            vm_code_12_25x26_31x6_11_lsl_2 = (cm.code_12_25 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2
            VM_REGS['m3'] = VM_REGS['m1'] + vm_code_12_25x26_31x6_11_lsl_2
            VM_REGS['m4'] = 2
            dispatch()

        elif cm.code_0_5 == 44:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            VM_REGS[f"m{op1_base_ptr-1}"] = reg_2_offset
            dispatch()
        
        elif cm.code_0_5 == 45:
            if vm_exec_state > 0:
                dispatch()
            if reg_1 == reg_2:
                # l217
                VM_REGS["m3"] = vm_code_ptr + 8 
                VM_REGS["m4"] = 1
            else:
                VM_REGS["m3"] = vm_code_ptr + ((cm.code_12_15 << 12 + cm.code_26_31 << 6 + cm.code_6_11) << 2)
                VM_REGS["m4"] = 2
            dispatch()
        
        elif cm.code_0_5 == 47:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
            v59 = (reg_2_offset & 0xFFFFFFFFFFFFFFFC).value()
            v60 = ((reg_2 + (cm.code_6_11 + cm.code_26_31 << 6)) << 3) & 0x18
            v52 = reg_1  & (0xFFFFFF >> v60) | (v59 << (0x18 - v60))
            VM_REGS[f"m{op1_base_ptr-1}"] = v52
            dispatch()
        
        elif cm.code_0_5 == 49:
            
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            logger.info(f"0_5:49, reg_{op1_base_ptr-1}, reg_{op2_base_ptr-1}, reg_2_offset={reg_2_offset}")
            write_mem(reg_2_offset.value(), reg_1)
            dispatch()
        
        elif cm.code_0_5 == 50:
            logger.info("Branch 50: STR VRm, [VRn, #offset]")
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
            logger.info(f"0_5:50, reg_{op1_base_ptr-1}, reg_{op2_base_ptr-1}, reg_{op2_base_ptr-1}_offset={hex(reg_2_offset)}")
            write_mem(reg_2_offset.value(), reg_1)
            dispatch()
        
        elif cm.code_0_5 == 51:
            # a6 
            vm_code_12_25_26_31_6_11 = cm.code_12_25 << 12 + cm.code_26_31 << 6 + cm.code_6_11
            fpr_call_handle = MEMORY_EFCC0[6 * vm_code_12_25_26_31_6_11 + 4] # 64bit?
            vm_code_6_11x26x27 = ((vm_code >> 0x14) &0x80) | ((vm_code >> 0x14) &0x40) | cm.code_6_11
            
            if vm_code_6_11x26x27 in (39,40,41):
                a6 = VM_REGS["m34"] # convert here # todo
                VM_REGS["m36"] = a6 & 0xffffffff

            elif vm_code_6_11x26x27 >= 42:
                if vm_code_12_25_26_31_6_11 >= 0x18:dispatch()
                #TODO FPR_HANDLE IMPLEMENTATION
                fpr_result = deref(fpr_call_handle)(VM_REGS['m34'], VM_REGS['m33'])
                VM_REGS["m36"] = fpr_result
            else:
                # implemented here
                ...
                
            dispatch()

        elif cm.code_0_5 == 52:
            #not sure possble dispatch
            dispatch()
        
        elif cm.code_0_5 == 53:
            # use complement
            logger.info("Branch 53: MOV VRd, VRm, #offset")
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement(cm.code_6_11 + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            VM_REGS[f"m{op1_base_ptr-1}"] = reg_2_offset
            logger.info(f"VRd: reg_{op1_base_ptr-1}, VRm: reg_{op2_base_ptr-1}, reg_{op2_base_ptr-1}_offset={hex(reg_2_offset)}")

            break
            dispatch()
        
        elif cm.code_0_5 == 54:
            """
                ???, i really don't know why lsl 16 here
            """
            VM_REGS[f"m{op1_base_ptr-1}"] = ((cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12)) << 16
            dispatch()

        elif cm.code_0_5 == 58:
            logger.info("Branch 58: LDR VRd, [VRm, #offset]")
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + complement(cm.code_6_11 + (cm.code_26_31 << 6) + (cm.code_12_15 << 12))
            #VM_REGS[f"m{op1_base_ptr-1}"] = reg_2_offset.value()
            logger.info(f"VRd: reg_{op1_base_ptr-1}, VRm: reg_{op2_base_ptr-1}, reg_{op2_base_ptr-1}_offset={hex(reg_2_offset)}")
            dispatch()
            break
        
        elif cm.code_0_5 == 60:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + (cm.code_6_11) + (cm.code_26_31 << 6) + (cm.code_12_15 << 12)
            VM_REGS[f"m{op1_base_ptr-1}"] = reg_2_offset
            dispatch()

        elif cm.code_0_5 == 62:
            reg_2_offset = VM_REGS[f"m{op2_base_ptr-1}"] + cm.code_6_11 + (cm.code_26_31 << 6) + (cm.code_12_15 << 12)
            v67 = reg_2_offset & 0xFFFFFFFFFFFFFFF8
            v69 = ((reg_2 + cm.code_6_11 + cm.code_26_31 << 6) << 3) & 0x38  # equals to (reg_2 + cm.code_6_11) & 0x7 
            buf = v67.value() & (0xFFFFFFFFFFFFFF00 << v69) | (VM_REGS[f"m{op1_base_ptr-1}"]  >> (0x38 - v69))
            write_mem(v67.value(), buf)
            dispatch()

        elif cm.code_0_5 == 63:
            if cm.code_0_11 == 319:
                if cm.code_26_31 == 22:
                    VM_REGS[f"m{op2_base_ptr-1}"] = SLOWORD(VM_REGS[f"m{op1_base_ptr-1}"]) 
                
                elif cm.code_26_31 == 17:
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"]
                    tmp_ptr = 38-cm.code_12_15
                    VM_REGS[f"m{tmp_ptr}"] = LODWORD(reg_1 << 8) & 0xff00ff00 | LODWORD(reg_1 >> 8) & 0xff00ff
                             
            elif cm.code_0_11 == 575:
                v1 = cm.code_26_30 | 0x20
                v2 = cm.code_12_15 | 0x20
                if v2 < v1: dispatch()
                reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                v3 = reg_1 & (0xFFFFFFFFFFFFFFFF << v2) | ((reg_2 & negate(0xFFFFFFFFFFFFFFFF << (v2 - v1 + 1))) << v1) | reg_1 & negate(0xFFFFFFFFFFFFFFFF << v1)
                VM_REGS[f"m{op1_base_ptr-1}"] = v3
            
            elif cm.code_0_11 == 767:
                if cm.code_26_30 + cm.code_12_15 <= 0x3f:
                    v1 = VM_REGS[f"m{op2_base_ptr-1}"]
                    if cm.code_12_15 != 0x3f:
                      v1 = (VM_REGS[f"m{op2_base_ptr-1}"] >> cm.code_26_30) & negate(0xFFFFFFFFFFFFFFFF << (cm.code_12_15 + 1))
                    VM_REGS[f"m{op1_base_ptr-1}"] = v1

            elif cm.code_0_11 == 959:
                v1 = cm.code_26_30 | 0x20
                v2 = cm.code_12_15 | 0x20
                if v2 < v1:dispatch()
                reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                v3 = reg_1 & (0xFFFFFFFFFFFFFFFF << v2) | ((reg_2 & negate(0xFFFFFFFFFFFFFFFF << (v2 - v1 + 1))) << v1) | reg_1 & negate(0xFFFFFFFFFFFFFFFF << v1)
                VM_REGS[f"m{op1_base_ptr-1}"] = v3
            
            elif cm.code_0_11 == 1471:
                if cm.code_26_30 > cm.code_12_15: dispatch()
                v1 = cm.code_26_30
                v2 = cm.code_12_15
                reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                v1 = reg_1 & (0xffffffff << v2) | (reg_2 & negate(0xffffffff << (v2 - v1 + 1))<<v1) | reg_1 & negate(0xffffffff << v1)
                VM_REGS[f"m{op1_base_ptr-1}"] = v1
            
            elif cm.code_0_11 == 1791:
                if cm.code_26_30 > cm.code_12_15: dispatch()
                reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                reg_2 = VM_REGS[f"m{op2_base_ptr-1}"]
                v1 = cm.code_26_30
                v2 = cm.code_12_15
                v3 = reg_1 & (0xFFFFFFFFFFFFFFFF << v2) | ((reg_2 & negate(0xFFFFFFFFFFFFFFFF << (v2 - v1 + 1))) << v1) | reg_1 & negate(0xFFFFFFFFFFFFFFFF << v1)
                VM_REGS[f"m{op1_base_ptr-1}"] = v1
            
            elif cm.code_0_11 == 2239:
                if cm.code_26_30 == 24:  #0b011000 [26:31]
                    reg_1 = VM_REGS[f"m{op1_base_ptr-1}"] 
                    tmp_ptr = 38-cm.code_12_15
                    VM_REGS[f"m{tmp_ptr}"] = ROR(((reg_1 << 0x10) & 0xffff0000ffff0000) | ((reg_1 >> 0x10) & 0xffff0000ffff), 32)

            elif cm.code_0_11 == 3007:
                v1 = cm.code_26_30 | 0x20
                if cm.v1 + cm.code_12_15 <= 0x3f:
                    v2 = VM_REGS[f"m{op2_base_ptr-1}"]
                    if cm.code_12_15 != 0x3f:
                      v2 = (VM_REGS[f"m{op2_base_ptr-1}"] >> v1) & negate(0xFFFFFFFFFFFFFFFF << (cm.code_12_15 + 1))
                    VM_REGS[f"m{op1_base_ptr-1}"] = v2

            elif cm.code_0_11 == 3647:
                if cm.code_26_30 + cm.code_12_15 <= 0x3f:
                    v1 = VM_REGS[f"m{op2_base_ptr-1}"] #TODO lodword regulation here
                    if cm.code_12_15 != 0x1f:
                        v1 = (VM_REGS[f"m{op2_base_ptr-1}"] >> cm.code_26_30) & negate(0xFFFFFFFE << cm.code_12_15)
                    VM_REGS[f"m{op1_base_ptr-1}"] = v1

            elif cm.code_0_11 == 4095:
                v1 = cm.code_12_15 | 0x20
                if cm.code_26_30 + v1 <= 0x3f:
                    v2 = VM_REGS[f"m{op2_base_ptr-1}"] #TODO lodword regulation here
                    if v1 != 0x3f:
                        v2 = (VM_REGS[f"m{op2_base_ptr-1}"] >> v1) & negate(0xFFFFFFFFFFFFFFFF << (cm.code_12_15 + 1))
                    VM_REGS[f"m{op1_base_ptr-1}"] = v2
                
            dispatch()
 
def vm_handle():
    ...

if __name__ == "__main__":
    
    vm_code = 0b11000011101111011110010000110101
    
    Vm([vm_code],0,0,0,[0,0,1],0)