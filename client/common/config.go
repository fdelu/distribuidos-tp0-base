package common

import (
	"time"

	log "github.com/sirupsen/logrus"
)

// Config Configuration used by the client
type Config struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
	BatchSize     int
	BetsFilePath  string
}

func (c *Config) Print() {
	log.Infof("action: config | result: success | %+v", c)
}
