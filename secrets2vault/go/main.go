package main

import (
	"bufio"
	"encoding/base64"
	"fmt"
	"os"
	"strings"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.SplitN(line, ": ", 2)
		if len(parts) != 2 {
			fmt.Fprintf(os.Stderr, "Invalid input: %s\n", line)
			continue
		}
		key := parts[0]
		encodedValue := parts[1]
		decodedValue, err := base64.StdEncoding.DecodeString(encodedValue)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error decoding base64: %v\n", err)
			continue
		}
		fmt.Printf("%s: %s\n", key, decodedValue)
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Error reading from stdin: %v\n", err)
	}
}
