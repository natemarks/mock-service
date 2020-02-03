package main

import (
	"testing"
)

func TestWaitResponse(t *testing.T) {
	res := WaitResponse("50ms")
	if res != "You waited for 50ms" {
		t.Fail()
	}
}
