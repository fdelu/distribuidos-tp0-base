package common

import (
	"encoding/binary"
	"io"
	"net"
	"sync/atomic"

	log "github.com/sirupsen/logrus"
)

// Client Entity that encapsulates how
type Client struct {
	config  Config
	conn    *net.TCPConn
	stopped atomic.Bool
}

const MAX_SIZE = 8000 // Max message size
const LEN_BYTES = 2   // How many bytes to use for the len of the message
// Make sure MAX_SIZE is less than 2^(8*LEN_BYTES)

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config Config) *Client {
	var stopped atomic.Bool
	stopped.Store(false)
	client := &Client{
		config:  config,
		stopped: stopped,
	}
	client.createClientSocket()
	return client
}

// createClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() {
	addr, _ := net.ResolveTCPAddr("tcp", c.config.ServerAddress)
	conn, err := net.DialTCP("tcp", nil, addr)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	log.Infof(
		"action: connect | result: success | client_id: %v",
		c.config.ID,
	)
	c.conn = conn
}

// Closes the internal socket. Calling this method more than once
// will do nothing.
func (c *Client) Close() {
	wasStopped := c.stopped.Swap(true)
	if wasStopped {
		return
	}

	c.conn.Close()
	c.conn = nil
}

// Sends a message to the server. Does nothing if closed.
// Adds a header of 2 bytes with the message length
func (c *Client) Send(message string) {
	if c.stopped.Load() {
		return
	}
	bytes := []byte(message)

	if len(bytes) > MAX_SIZE {
		log.Fatalf("Tried to send a message of more than %d bytes (%d bytes)", MAX_SIZE, len(bytes))
	}

	binary.Write(c.conn, binary.BigEndian, uint16(len(bytes)))

	for totalSent := 0; totalSent < len(bytes); {
		sent, e := c.conn.Write(bytes[totalSent:])
		if e != nil {
			log.Error("action: send_message | result: failed | client_id: %v | error: %s",
				c.config.ID,
				e)
			return
		}
		totalSent += sent
	}
	log.Trace("action: send_message | result: success | client_id: %v",
		c.config.ID)
}

// Receives a message to the server. Returns an empty string if closed
func (c *Client) Receive() string {
	if c.conn == nil {
		return ""
	}

	sizeBuf := make([]byte, 2)
	_, err := io.ReadFull(c.conn, sizeBuf)
	if err != nil {
		log.Fatalf("Failed to read from socket: %s", err)
	}
	size := binary.BigEndian.Uint16(sizeBuf)
	msgBuf := make([]byte, size)
	_, err = io.ReadFull(c.conn, msgBuf)
	if err != nil {
		log.Fatalf("Failed to read from socket: %s", err)
	}
	log.Tracef("Reading message of size %d: %s", size, string(msgBuf))

	return string(msgBuf)
}
