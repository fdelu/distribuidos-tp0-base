package common

import (
	"encoding/binary"
	"net"

	log "github.com/sirupsen/logrus"
)

// Client Entity that encapsulates how
type Client struct {
	config Config
	conn   *net.TCPConn
}

const MAX_SIZE = 8000 // Max message size
const LEN_BYTES = 2   // How many bytes to use for the len of the message
// Make sure MAX_SIZE is less than 2^(8*LEN_BYTES)

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config Config) *Client {
	client := &Client{
		config: config,
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
	c.conn = conn
}

// Closes the internal socket. Calling this method more than once
// will do nothing.
func (c *Client) Close() {
	if c.conn == nil {
		return
	}

	c.conn.Close()
	c.conn = nil
	log.Infof("action: disconnect | result: success | client_id: %v",
		c.config.ID,
	)
}

// Sends a message to the server. Does nothing if closed.
// Adds a header of 2 bytes with the message length
func (c *Client) Send(data []byte) {
	if c.conn == nil {
		return
	}
	if len(data) > MAX_SIZE {
		log.Fatalf("Tried to send a message of more than %d bytes (%d bytes)", MAX_SIZE, len(data))
	}

	binary.Write(c.conn, binary.BigEndian, uint16(len(data)))

	for totalSent := 0; totalSent < len(data); {
		sent, _ := c.conn.Write([]byte(data[totalSent:]))
		totalSent += sent
	}
	log.Infof("action: send_message | result: success | client_id: %v",
		c.config.ID)
}
