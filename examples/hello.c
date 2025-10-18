#include <stdio.h>
#include <string.h>

const char* greeting = "Hello, ObfuscateLLVM!";
const char* message = "This is a test program for obfuscation.";

int main(int argc, char* argv[]) {
    printf("%s\n", greeting);
    printf("%s\n", message);
    
    if (argc > 1) {
        printf("Arguments provided: %d\n", argc - 1);
        for (int i = 1; i < argc; i++) {
            printf("  Arg %d: %s\n", i, argv[i]);
        }
    }
    
    // Simple computation to test obfuscation
    int sum = 0;
    for (int i = 1; i <= 10; i++) {
        sum += i;
    }
    printf("Sum of 1-10: %d\n", sum);
    
    return 0;
}