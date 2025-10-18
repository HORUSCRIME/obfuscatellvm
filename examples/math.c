#include <stdio.h>
#include <math.h>

// Function to test control flow obfuscation
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Function with multiple branches for CFG testing
int classify_number(int num) {
    if (num < 0) {
        return -1; // negative
    } else if (num == 0) {
        return 0;  // zero
    } else if (num % 2 == 0) {
        return 2;  // positive even
    } else {
        return 1;  // positive odd
    }
}

int main() {
    const char* title = "Mathematical Operations Test";
    printf("%s\n", title);
    printf("========================\n");
    
    // Test fibonacci
    printf("Fibonacci sequence (first 10 numbers):\n");
    for (int i = 0; i < 10; i++) {
        printf("fib(%d) = %d\n", i, fibonacci(i));
    }
    
    // Test number classification
    printf("\nNumber classification:\n");
    int test_numbers[] = {-5, 0, 3, 8, 15, -2};
    int num_tests = sizeof(test_numbers) / sizeof(test_numbers[0]);
    
    for (int i = 0; i < num_tests; i++) {
        int num = test_numbers[i];
        int result = classify_number(num);
        const char* type;
        
        switch (result) {
            case -1: type = "negative"; break;
            case 0:  type = "zero"; break;
            case 1:  type = "positive odd"; break;
            case 2:  type = "positive even"; break;
            default: type = "unknown"; break;
        }
        
        printf("%d is %s\n", num, type);
    }
    
    return 0;
}