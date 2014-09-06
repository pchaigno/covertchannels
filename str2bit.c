#include <stdio.h>

#define NB_LETTER 12

void str2bit(char* str, int* bits);
void bit2str(int* bits, char* str);

int main() {
	int bits[8 * NB_LETTER];
	char str[NB_LETTER + 1];
	str2bit("HELLO", bits);
	bit2str(bits, str);
	printf("%s\n", str);
	return 0;
}

void str2bit(char* str, int* bits) {
	int i;
	for(i=0; i<8*NB_LETTER; i++) {
		bits[i] = (0 != (str[i / 8] & 1 << (~i & 7)));
	}
}

void bit2str(int* bits, char* str) {
	int i;
	int expo[] = {128, 64, 32, 16, 8, 4, 2, 1};
	for(i=0; i<NB_LETTER; i++) {
		str[i] = 0;
	}
	for(i=0; i<8*NB_LETTER; i++) {
		str[i / 8] += bits[i] * expo[i%8];
	}
	str[NB_LETTER] = '\0';
}
