package common

import (
	"encoding/csv"
	"encoding/json"
	"io"
	"os"
	"os/signal"
	"syscall"

	log "github.com/sirupsen/logrus"
)

type Agency struct {
	config     Config
	client     *Client
	betsFile   *os.File
	betsReader *csv.Reader
}

func NewAgency(config Config) *Agency {
	return &Agency{config: config}
}

func (a *Agency) stop() {
	a.client.Close()
	if a.betsFile != nil {
		a.betsFile.Close()
	}
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
	if a.betsReader == nil {
		if a.betsFile == nil {
			return bets
		}
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
		response := ParseResultMessage(a.client.Receive())
		log.Debugf("action: sent_bets | result: %s | amount: %d", response, len(bets))
		total_sent += len(bets)
	}

	log.Infof("action: disconnect | submitted: %d | result: success | client_id: %v",
		total_sent,
		a.config.ID,
	)
	a.stop()
}
