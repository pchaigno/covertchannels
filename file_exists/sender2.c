#include <stdio.h>
#include <unistd.h>
#include <string.h>

#define TRANSMITTING "/tmp/transmitting"
#define DATA "/tmp/data"
#define READING "/tmp/reading"
#define WRITING "/tmp/writing"
#define SAW_WRITING "/tmp/saw_writing"
#define SAW_READING "/tmp/saw_reading"

void create_file(char* file);
void writeBit(int bit);
void str2bit(char* str, int* bits, int nbLetters);

int lastBit = -1;

int main() {
	// Initializes the string to send:
	char* str = "Hello World, Hello RIT! This is not a very stealthy covert channel...";
	int nbLetters = strlen(str);
	int data[nbLetters * 8];
	int i;
	str2bit(str, data, nbLetters);

	create_file(TRANSMITTING);
	for(i=0; i<nbLetters * 8; i++) {
		create_file(WRITING);
		writeBit(data[i]);
		while(!file_exists(SAW_WRITING));
		remove(WRITING);

		while(!file_exists(READING));
		create_file(SAW_READING);
		while(file_exists(READING));
		remove(SAW_READING);
	}

	// Cleans up:
	remove(TRANSMITTING);
	remove(WRITING);
	remove(SAW_READING);

	printf("%d letters sent (%d bits)!\n", nbLetters, nbLetters * 8);

	return 0;
}

/**
 * Creates a file.
 * @param file The path to the file.
 */
void create_file(char* file) {
	FILE *fp;
	fp = fopen(file, "w+");
	fclose(fp);
}

/**
 * Checks if a file exists.
 * @param file The path to the file.
 * @return True if the file exists.
 */
int file_exists(char* file) {
	return access(file, F_OK) != -1;
}

/**
 * "Writes" a bit.
 * I.e., creates or removes the DATA file respectively for a 1 or 0.
 * @param bit The bit to write.
 */
void writeBit(int bit) {
	if(bit == lastBit) {
		return;
	}
	lastBit = bit;
	if(bit) {
		FILE *fp;
		fp = fopen("/tmp/data", "w+");
		fclose(fp);
	} else {
		remove("/tmp/data");
	}
}

/**
 * Converts an ASCII string into an array of bits.
 * @param str The ASCII string.
 * @param bits The array of bits as integers.
 * @param nbLetters The number of letters in the ASCII string.
 */
void str2bit(char* str, int* bits, int nbLetters) {
	int i;
	for(i=0; i<nbLetters*8; i++) {
		bits[i] = (0 != (str[i / 8] & 1 << (~i & 7)));
	}
}