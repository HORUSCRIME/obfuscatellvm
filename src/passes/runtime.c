// Runtime support functions for obfuscated binaries

#include <stdlib.h>
#include <string.h>

// String decryption function
char* decrypt_string(const char* encrypted, unsigned char key, int length) {
    static char buffer[1024];
    if (length >= sizeof(buffer)) {
        return NULL;
    }
    
    for (int i = 0; i < length; i++) {
        buffer[i] = encrypted[i] ^ key;
    }
    buffer[length] = '\0';
    
    return buffer;
}