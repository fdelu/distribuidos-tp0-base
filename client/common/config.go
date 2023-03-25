package common

import (
	"time"
)

// Config Configuration used by the client
type Config struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}
