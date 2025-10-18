// VM runtime for function virtualization

#include <stdint.h>

// VM opcodes
#define VM_LOAD  1
#define VM_STORE 2
#define VM_ADD   3
#define VM_SUB   4
#define VM_MUL   5
#define VM_RET   6

// Simple stack-based VM interpreter
int vm_interpret(const uint8_t* bytecode, int length) {
    int stack[256];
    int sp = 0;  // Stack pointer
    int pc = 0;  // Program counter
    int result = 0;
    
    while (pc < length) {
        uint8_t opcode = bytecode[pc++];
        
        switch (opcode) {
            case VM_LOAD:
                if (sp < 255) {
                    stack[sp++] = 42; // Dummy value
                }
                break;
                
            case VM_STORE:
                if (sp > 0) {
                    result = stack[--sp];
                }
                break;
                
            case VM_ADD:
                if (sp >= 2) {
                    int b = stack[--sp];
                    int a = stack[--sp];
                    stack[sp++] = a + b;
                }
                break;
                
            case VM_SUB:
                if (sp >= 2) {
                    int b = stack[--sp];
                    int a = stack[--sp];
                    stack[sp++] = a - b;
                }
                break;
                
            case VM_MUL:
                if (sp >= 2) {
                    int b = stack[--sp];
                    int a = stack[--sp];
                    stack[sp++] = a * b;
                }
                break;
                
            case VM_RET:
                if (sp > 0) {
                    result = stack[--sp];
                }
                return result;
                
            default:
                return 0; // Unknown opcode
        }
    }
    
    return result;
}