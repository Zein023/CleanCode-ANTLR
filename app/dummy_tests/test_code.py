# test_code.py

# 1. Shadowing Built-in
list = [1, 2, 3] 

def fungsibersih(param1, param2, param3, param4): # 2. PascalCase & Too Many Args
    
    # 3. Shadowing Outer Scope
    list = "shadowing" 
    
    # 4. Deep Nesting
    if param1:
        if param2:
            if param3:
                if param4:
                    if param1:
                        if param2:
                            print("Too deep!")

def complex_logic(x):
    # 5. High Complexity (Score awal 1 + 5 if = 6)
    if x == 1: pass
    if x == 2: pass
    if x == 3: pass
    if x == 4: pass
    if x == 5: pass