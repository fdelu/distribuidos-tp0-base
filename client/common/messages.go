package common

import (
	"encoding/json"
	"log"
)

type Message[T any] struct {
	Type    string `json:"type"`
	Payload T      `json:"payload"`
}

// Client messages
const SUBMIT_TYPE = "submit"
const GET_WINNERS_TYPE = "get_winners"

func SubmitBetsMessage(bets []Bet) Message[[]Bet] {
	return Message[[]Bet]{
		Type:    SUBMIT_TYPE,
		Payload: bets,
	}
}

func GetWinnersMessage() Message[any] {
	return Message[any]{
		Type: GET_WINNERS_TYPE,
	}
}

// Server messages
const SUBMIT_RESULT_TYPE = "submit_result"
const WINNERS_TYPE = "winners"

func parseMessage[T any](msg string, expectedType string) T {
	result := &Message[T]{}
	json.Unmarshal([]byte(msg), result)
	if result.Type != expectedType {
		log.Fatalf("Expected message of type %s from server but got type %s", expectedType, result.Type)
	}
	return result.Payload
}

func ParseWinnersMessage(msg string) []Dni {
	return parseMessage[[]Dni](msg, WINNERS_TYPE)
}

func ParseResultMessage(msg string) string {
	return parseMessage[string](msg, SUBMIT_RESULT_TYPE)
}
