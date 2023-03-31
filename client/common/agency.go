package common

import (
	"encoding/csv"
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

// Exits the program. Closes the client socket and the bets file
func (a *Agency) stop() {
	wasStopped := a.stopped.Swap(true)
	if wasStopped {
		return
	}
	a.client.Close()
	log.Infof("action: disconnected | client_id: %v",
		a.config.ID,
	)
	a.betsFile.Close()
}

// Sets up the SIGTERM signal to stop the process
func (a *Agency) setupStop() {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM)
	go func() {
		<-stop
		a.stop()
		os.Exit(0)
	}()
}

// Reads a batch of bets from the csv file
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

// Sends all of the bets from the file to the server in batchs.
func (a *Agency) sendBets() {
	total_sent := 0
	result := "success"
	for bets := a.readBatch(); len(bets) > 0; bets = a.readBatch() {
		message := NewSubmitMessage(bets).ToString()
		a.client.Send(string(message))
		response := a.client.Receive()
		if response == "" {
			result = "failed"
			break
		}
		result := SubmitResultMessageFromString(response)
		log.Debugf("action: submit_bets | result: %s | amount: %d", result.Payload, len(bets))
		total_sent += len(bets)
	}
	log.Infof("action: completed_submit_bets | total_submitted: %d | result: %s | client_id: %v",
		total_sent,
		result,
		a.config.ID,
	)
}

// Sends a request to the server to get the winner documents for this agency,
// and logs the amount of winners.
func (a *Agency) getWinners() {
	message := NewGetWinnersMessage().ToString()
	a.client.Send(string(message))

	response := a.client.Receive()
	if response == "" {
		return
	}
	winners := WinnersMessageFromString(response).Payload
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d", len(winners))
}

// Runs the Agency: sends all of the bets to the server and gets the winners.
func (a *Agency) Run() {
	a.setupStop()
	a.client = NewClient(a.config)
	bets, err := os.Open(a.config.BetsFilePath)
	if err != nil {
		log.Fatal(err)
	}
	a.betsFile = bets

	a.sendBets()
	a.getWinners()
	a.stop()
}
