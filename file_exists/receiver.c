#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

#define DATA "/tmp/data"
#define READ "/tmp/read"
#define WRITTEN "/tmp/written"
#define RECEIVER_READY "/tmp/receiver_ready"
#define SENDER_READY "/tmp/sender_ready"
#define FINISHED "/tmp/finished"

void bit2str(int* bits, char* str, int nbLetters);

int main() {
	int bits[1000];
	int nb = 0;

	while(!file_exists(WRITTEN));

	// Records the current time at the beginning of the transmission:
	struct timeval tv1, tv2;
	gettimeofday(&tv1, NULL);
	
	while(!file_exists(FINISHED)) {
		remove(READY);
		int data = file_exists(DATA);
		create_file(READ);
		bits[nb] = data;
		nb++;

		while(!file_exists(SENDER_READY));
		remove(READ);
		create_file(RECEIVER_READY);

		while(!file_exists(WRITTEN) && !file_exists(FINISHED));
	}

	// Computes the duration of the transmission:
	gettimeofday(&tv2, NULL);
	double time_spent = (double)(tv2.tv_usec - tv1.tv_usec) / 1000 + (double)(tv2.tv_sec - tv1.tv_sec) * 1000;
	printf("Total time: %fms\n", time_spent);

	// Converts and print the received string:
	char str[nb / 8 + 1];
	bit2str(bits, str, nb / 8);
	printf("%s\n", str);

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