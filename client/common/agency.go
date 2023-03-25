package common

import (
	"encoding/json"
	"os"
	"os/signal"
	"syscall"
)

type Agency struct {
	config Config
	client *Client
}

func NewAgency(config Config) *Agency {
	return &Agency{config: config}
}

func (a *Agency) setupStop() {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM)
	go func() {
		<-stop
		if a.client != nil {
			a.client.Close()
		}
	}()
}

func (a *Agency) Run() {
	a.setupStop()
	a.client = NewClient(a.config)

	apuesta := BetFromEnv()
	message, _ := json.Marshal(apuesta)
	a.client.Send(string(message))
	a.client.Close()
}
