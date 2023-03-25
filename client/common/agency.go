package common

import (
	"encoding/csv"
	"encoding/json"
	"io"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"

	log "github.com/sirupsen/logrus"
)

type Agency struct {
	config     Config
	client     *Client
	betsFile   *os.File
	betsReader *csv.Reader
	stopped    atomic.Bool
}

func NewAgency(config Config) *Agency {
	var stopped atomic.Bool
	stopped.Store(false)
	return &Agency{config: config, stopped: stopped}
}

func (a *Agency) stop() {
	wasStopped := a.stopped.Swap(true)
	if wasStopped {
		return
	}
	a.client.Close()
	a.betsFile.Close()
	log.Infof("action: disconnected | client_id: %v",
		a.config.ID,
	)
}

func (a *Agency) setupStop() {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM)
	go func() {
		<-stop
		a.stop()
	}()
}

func (a *Agency) readBatch() []Bet {
	bets := []Bet{}
	if a.stopped.Load() {
		return bets
	}
	if a.betsReader == nil {
		a.betsReader = csv.NewReader(a.betsFile)
	}

	for i := 0; i < a.config.BatchSize; i++ {
		line, err := a.betsReader.Read()
		if err == io.EOF {
			return bets
		}
		if err != nil {
			log.Fatal(err)
		}
		// log.Debug(line)
		bet := NewBet(line[4], line[2], line[1], line[2], line[3], a.config.ID)
		bets = append(bets, *bet)
	}
	return bets
}

func (a *Agency) Run() {
	a.setupStop()
	a.client = NewClient(a.config)
	bets, err := os.Open(a.config.BetsFilePath)
	if err != nil {
		log.Fatal(err)
	}
	a.betsFile = bets

	total_sent := 0
	for bets := a.readBatch(); len(bets) > 0; bets = a.readBatch() {
		message, _ := json.Marshal(SubmitBetsMessage(bets))
		a.client.Send(string(message))
		response := a.client.Receive()
		if response == "" {
			break
		}
		result := ParseResultMessage(response)
		log.Debugf("action: submit_bets | result: %s | amount: %d", result, len(bets))
		total_sent += len(bets)
	}
	log.Infof("action: completed_submit_bets | total_submitted: %d | result: success | client_id: %v",
		total_sent,
		a.config.ID,
	)
	a.stop()
}
