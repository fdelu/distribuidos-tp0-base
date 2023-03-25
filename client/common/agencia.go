package common

import (
	"os"
	"os/signal"
	"syscall"
)

type Agencia struct {
	config Config
	client *Client
}

func NewAgencia(config Config) *Agencia {
	return &Agencia{config: config}
}

func (a *Agencia) setupStop() {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM)
	go func() {
		<-stop
		if a.client != nil {
			a.client.Close()
		}
	}()
}

func (a *Agencia) Run() {
	a.setupStop()
	a.client = NewClient(a.config)

	apuesta := ApuestaFromEnv()
	a.client.Send([]byte(apuesta.ToJson()))
	a.client.Close()
}
