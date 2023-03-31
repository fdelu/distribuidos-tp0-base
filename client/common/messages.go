package common

import (
	"log"
	"strings"
)

type SubmitMessage struct{ Payload []Bet }
type GetWinnersMessage struct{}
type SubmitResultMessage struct{ Payload string }
type WinnersMessage struct{ Payload []Dni }

type MessageType = string

const (
	// Client messages
	SUBMIT      MessageType = "S"
	GET_WINNERS MessageType = "G"

	// Server messages
	SUBMIT_RESULT MessageType = "R"
	WINNERS       MessageType = "W"

	SPLIT_CHAR = "\n"
)

func NewSubmitMessage(bets []Bet) *SubmitMessage {
	return &SubmitMessage{bets}
}

func (m *SubmitMessage) ToString() string {
	betsString := []string{}
	for i := 0; i < len(m.Payload); i++ {
		betsString = append(betsString, m.Payload[i].ToString())
	}
	return SUBMIT + strings.Join(betsString, SPLIT_CHAR)
}

func NewGetWinnersMessage() *GetWinnersMessage {
	return &GetWinnersMessage{}
}

func (m *GetWinnersMessage) ToString() string {
	return GET_WINNERS
}

func splitMessage(msg string, expectedType MessageType) string {
	msgType := msg[0:1]
	if msgType != expectedType {
		log.Fatalf("Expected message of type %s from server but got type %s", expectedType, msgType)
	}
	return msg[1:]
}

func WinnersMessageFromString(msg string) *WinnersMessage {
	dnis := splitMessage(msg, WINNERS)
	return &WinnersMessage{
		strings.Split(dnis, SPLIT_CHAR),
	}
}

func SubmitResultMessageFromString(msg string) *SubmitResultMessage {
	result := splitMessage(msg, SUBMIT_RESULT)
	return &SubmitResultMessage{
		result,
	}
}
