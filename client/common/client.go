package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   *net.TCPConn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	addr, _ := net.ResolveTCPAddr("tcp", c.config.ServerAddress)
	conn, err := net.DialTCP("tcp", nil, addr)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// autoincremental msgID to identify every message sent
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM)
	msgID := 1

	periodTimer := time.After(0) // First iteration does not wait

loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeoutTimer := time.After(c.config.LoopLapse); ; {
		select {
		case <-timeoutTimer:
			log.Infof("action: timeout_detected | result: success | client_id: %v",
				c.config.ID,
			)
			break loop
		case <-stop:
			log.Infof("action: stop_received | result: success | client_id: %v",
				c.config.ID,
			)
			break loop
		case <-periodTimer:
		}

		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		toSend := []byte(fmt.Sprintf(
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		))
		for total_sent := 0; total_sent < len(toSend); {
			sent, _ := c.conn.Write([]byte(toSend))
			total_sent += sent
		}
		c.conn.CloseWrite()

		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		msgID++
		c.conn.Close()
		log.Infof("action: disconnect | result: success | client_id: %v",
			c.config.ID,
		)

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)

		// Wait a time between sending one message and the next one
		periodTimer = time.After(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
