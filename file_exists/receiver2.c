#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

#define TRANSMITTING "/tmp/transmitting"
#define DATA "/tmp/data"
#define READING "/tmp/reading"
#define WRITING "/tmp/writing"
#define SAW_WRITING "/tmp/saw_writing"
#define SAW_READING "/tmp/saw_reading"

void bit2str(int* bits, char* str, int nbLetters);

int main() {
	int bits[1000];
	int nb = 0;

	while(!file_exists(WRITING));

	// Records the current time at the beginning of the transmission:
	struct timeval tv1, tv2;
	gettimeofday(&tv1, NULL);

	while(file_exists(TRANSMITTING)) {
		create_file(SAW_WRITING);
		while(file_exists(WRITING));
		remove(SAW_WRITING);

		create_file(READING);
		int data = file_exists(DATA);
		while(!file_exists(SAW_READING));
		remove(READING);
		bits[nb] = data;
		nb++;

		while(!file_exists(WRITING) && file_exists(TRANSMITTING));
	}

	// Computes the duration of the transmission:
	gettimeofday(&tv2, NULL);
	double time_spent = (double)(tv2.tv_usec - tv1.tv_usec) / 1000 + (double)(tv2.tv_sec - tv1.tv_sec) * 1000;
	printf("Total time: %fms\n", time_spent);

	// Converts and print the received string:
	char str[nb / 8 + 1];
	bit2str(bits, str, nb / 8);
	printf("%s\n", str);

	// Cleans up:
	remove(SAW_WRITING);
	remove(READING);

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
 * Converts an array of bits into an ASCII string.
 * @param bits The array of bits as integers.
 * @param str The ASCII string.
 * @param nbLetters The number of letters in the ASCII string.
 */
void bit2str(int* bits, char* str, int nbLetters) {
	int i;
	int expo[] = {128, 64, 32, 16, 8, 4, 2, 1};
	for(i=0; i<nbLetters; i++) {
		str[i] = 0;
	}
	for(i=0; i<8 * nbLetters; i++) {
		str[i / 8] += bits[i] * expo[i%8];
	}
	str[nbLetters] = '\0';
}